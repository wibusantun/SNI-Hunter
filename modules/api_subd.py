from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from bs4 import BeautifulSoup
from threading import Lock
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn
import re
import os

console = Console()
file_write_lock = Lock()
session = requests.Session()
DEFAULT_TIMEOUT = 10

# Function to clear the terminal and display dynamic ASCII banner
def show_banner():
    os.system("clear")  # Use 'cls' for Windows
    try:
        # Get terminal width
        terminal_width = os.get_terminal_size().columns
    except OSError:
        # Fallback to a default width if terminal size cannot be determined
        terminal_width = 80

    # ASCII Art Banner
    banner = """

 ╔═══╦╗─╔╦══╗╔═══╗──────╔╗╔╗──╔═══╦═══╦══╗
 ║╔═╗║║─║║╔╗║╚╗╔╗║─────╔╝╚╣║──║╔═╗║╔═╗╠╣╠╝
 ║╚══╣║─║║╚╝╚╗║║║║╔╗╔╗╔╬╗╔╣╚═╗║║─║║╚═╝║║║
 ╚══╗║║─║║╔═╗║║║║║║╚╝╚╝╠╣║║╔╗║║╚═╝║╔══╝║║
 ║╚═╝║╚═╝║╚═╝╠╝╚╝║╚╗╔╗╔╣║╚╣║║║║╔═╗║║──╔╣╠╗
 ╚═══╩═══╩═══╩═══╝─╚╝╚╝╚╩═╩╝╚╝╚╝─╚╩╝──╚══╝
    """
    # Center-align banner
    centered_banner = "\n".join(line.center(terminal_width) for line in banner.splitlines())
    console.print(f"[bold cyan]{centered_banner}[/bold cyan]")

# Validate domain using regex
def validate_domain(domain):
    domain_pattern = re.compile(
        r"^(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,6}$"  # Matches domains like example.com, test.co.uk
    )
    return bool(domain_pattern.match(domain))

# Clean wildcard subdomains (e.g. *.example.com)
def clean_subdomain(subdomain):
    if subdomain.startswith("*."):
        return subdomain[2:]  # Remove wildcard from subdomain
    return subdomain

# Fetch subdomains from CRT.sh
def crtsh_subdomains(domain):
    subdomains = set()
    response = session.get(f"https://crt.sh/?q=%25.{domain}&output=json", timeout=DEFAULT_TIMEOUT)
    if response.status_code == 200 and response.headers.get('Content-Type') == 'application/json':
        for entry in response.json():
            subdomains.update(entry['name_value'].splitlines())
    return subdomains

# Fetch subdomains from HackerTarget
def hackertarget_subdomains(domain):
    subdomains = set()
    response = session.get(f"https://api.hackertarget.com/hostsearch/?q={domain}", timeout=DEFAULT_TIMEOUT)
    if response.status_code == 200 and 'text' in response.headers.get('Content-Type', ''):
        subdomains.update([line.split(",")[0] for line in response.text.splitlines()])
    return subdomains

# Fetch subdomains from RapidDNS
def rapiddns_subdomains(domain):
    subdomains = set()
    response = session.get(f"https://rapiddns.io/subdomain/{domain}?full=1", timeout=DEFAULT_TIMEOUT)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        for link in soup.find_all('td'):
            text = link.get_text(strip=True)
            if text.endswith(f".{domain}"):
                subdomains.add(text)
    return subdomains

# Fetch subdomains using AnubisDB
def anubisdb_subdomains(domain):
    subdomains = set()
    response = session.get(f"https://jldc.me/anubis/subdomains/{domain}", timeout=DEFAULT_TIMEOUT)
    if response.status_code == 200:
        subdomains.update(response.json())
    return subdomains

# Fetch subdomains using AlienVault
def alienvault_subdomains(domain):
    subdomains = set()
    response = session.get(f"https://otx.alienvault.com/api/v1/indicators/domain/{domain}/passive_dns", timeout=DEFAULT_TIMEOUT)
    if response.status_code == 200:
        for entry in response.json().get("passive_dns", []):
            subdomains.add(entry.get("hostname"))
    return subdomains

# Fetch subdomains using URLScan
def urlscan_subdomains(domain):
    subdomains = set()
    url = f"https://urlscan.io/api/v1/search/?q=domain:{domain}"
    response = session.get(url, timeout=DEFAULT_TIMEOUT)
    if response.status_code == 200:
        for result in response.json().get('results', []):
            page_url = result.get('page', {}).get('domain')
            if page_url and page_url.endswith(f".{domain}"):
                subdomains.add(page_url)
    return subdomains

# Fetch subdomains using C99 Subdomain Finder
def c99_subdomains(domain):
    subdomains = set()
    response = session.get(f"https://subdomainfinder.c99.nl/scans/{datetime.now().strftime('%Y-%m-%d')}/{domain}", timeout=DEFAULT_TIMEOUT)
    if response.status_code == 200:
        subdomains.update(response.text.splitlines())
    return subdomains

# Fetch subdomains using provided function
def fetch_subdomains(source_func, domain):
    try:
        return source_func(domain)
    except Exception as e:
        console.print(f"[bold red]Error fetching subdomains for {domain} using {source_func.__name__}: {str(e)}[/bold red]")
        return set()

# Process each domain to fetch subdomains from all sources
def process_domain(domain, sources, output_file, progress, task_id):
    subdomains = set()
    console.print(f"[bold yellow]Fetching subdomains for:[/bold yellow] [bold blue]{domain}[/bold blue]")

    for source in sources:
        fetched_subdomains = fetch_subdomains(source, domain)
        cleaned_subdomains = {clean_subdomain(sub) for sub in fetched_subdomains}
        subdomains.update(cleaned_subdomains)
        progress.update(task_id, advance=1)

    # Safely write subdomains to file
    with file_write_lock:
        try:
            with open(output_file, "a", encoding="utf-8") as file:
                for subdomain in sorted(subdomains):
                    file.write(f"{subdomain}\n")
        except IOError as e:
            console.print(f"[bold red]Error writing to file: {e}[/bold red]")

    return subdomains

# Main function to find subdomains
def find_subdomains():
    # Show the dynamic ASCII banner
    show_banner()

    sources = [
        crtsh_subdomains, hackertarget_subdomains, rapiddns_subdomains,
        anubisdb_subdomains, alienvault_subdomains, urlscan_subdomains,
        c99_subdomains
    ]

    console.print("[bold yellow][1] Single domain[/bold yellow]")
    console.print("[bold yellow][2] Multiple domains[/bold yellow]")

    console.print("[bold green]» Enter your choice: [/bold green]", end="")
    choice = input().strip()

    # Handle single domain input
    if choice == '1':
        console.print("[bold green]» Enter domain: [/bold green]", end="")
        domain = input().strip()
        if not domain or not validate_domain(domain):
            console.print("[bold red]⚠ Invalid domain format or empty domain.[/bold red]")
            return
        domains = [domain]

    # Handle multiple domains input from file
    elif choice == '2':
        console.print("[bold green]» Enter file path: [/bold green]", end="")
        file_path = input().strip()
        if not os.path.exists(file_path):
            console.print("[bold red]⚠ File not found.[/bold red]")
            return
        try:
            with open(file_path, "r") as file:
                domains = [line.strip() for line in file if line.strip()]
        except Exception as e:
            console.print(f"[bold red]⚠ Error reading file: {e}[/bold red]")
            return

    else:
        console.print("[bold red]⚠ Invalid choice.[/bold red]")
        return

    # Ask user for output file name
    console.print("[bold green]» Enter output file name (without extension): [/bold green]", end="")
    output_file_name = input().strip()
    if not output_file_name:
        console.print("[bold red]⚠ Output file name cannot be empty.[/bold red]")
        return

    # Define output file path
    output_directory = "/storage/emulated/0/"
    output_file = os.path.join(output_directory, f"{output_file_name}.txt")

    console.print(f"[bold yellow]Starting subdomain finding...[/bold yellow]")
    total_tasks = len(domains) * len(sources)
    total_subdomains = 0

    # Use the rich library's Progress bar for real-time feedback
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[bold blue]{task.completed}/{task.total}"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task_id = progress.add_task("Processing", total=total_tasks)

        # Execute subdomain fetching concurrently
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                executor.submit(process_domain, domain, sources, output_file, progress, task_id): domain for domain in domains
            }
            for future in as_completed(futures):
                total_subdomains += len(future.result())

    console.print(f"\n[bold green] Subdomains saved in {output_file}[/bold green]")
    console.print(f"[bold green] Total subdomains found: {total_subdomains}[/bold green]")

    # Pause before exiting
    input(f"\nPress Enter to exit...")

if __name__ == "__main__":
    find_subdomains()