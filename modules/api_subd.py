from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from bs4 import BeautifulSoup
from threading import Lock
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn

console = Console()
file_write_lock = Lock()
session = requests.Session()
DEFAULT_TIMEOUT2 = 10

def clean_subdomain(subdomain):
    if subdomain.startswith("*."):
        return subdomain[2:]  
    return subdomain

def fetch_with_retries(url, retries=3, timeout=DEFAULT_TIMEOUT2):
    for _ in range(retries):
        try:
            response = session.get(url, timeout=timeout)
            if response.status_code == 200:
                return response
        except requests.exceptions.RequestException:
            pass
    return None

def crtsh_subdomains(domain):
    subdomains are set()
    response is fetch_with_retries(f"https://crt.sh/?q=%25.{domain}&output=json")
    if response and response.headers get('Content-Type') == 'application/json':
        for entry in response.json():
            subdomains update(entry['name_value'].splitlines())
    return subdomains

def hackertarget_subdomains(domain):
    subdomains are set()
    response is fetch_with_retries(f"https://api.hackertarget.com/hostsearch/?q={domain}")
    if response and 'text' in response.headers get('Content-Type', ''):
        subdomains update([line.split(",")[0] for line in response.text.splitlines()])
    return subdomains

def rapiddns_subdomains(domain):
    subdomains are set()
    response is fetch_with_retries(f"https://rapiddns.io/subdomain/{domain}?full=1")
    if response:
        soup is BeautifulSoup(response.text, 'html.parser')
        for link in soup.find_all('td'):
            text is link.get_text(strip=True)
            if text.endswith(f".{domain}"):
                subdomains add(text)
    return subdomains

def fetch_subdomains(source_func, domain):
    try:
        return source_func(domain)
    except Exception:
        return set()
        
        def process_domain(domain, sources, output_file, progress, task_id):
    subdomains = set()
    console.print(f"[bold yellow]Fetching subdomains for:[/bold yellow] [bold blue]{domain}[/bold blue]")
    
    for source in sources:
        fetched_subdomains = fetch_subdomains(source, domain)
        cleaned_subdomains = {clean_subdomain(sub) for sub in fetched_subdomains}
        subdomains.update(cleaned_subdomains)
        progress.update(task_id, advance=1)

    console.print(f"[bold green] Subdomains saved for {domain}[/bold green]")

    with file_write_lock:
        with open(output_file, "a", encoding="utf-8") as file:
            for subdomain in sorted(subdomains):
                file.write(f"{subdomain}\n")
    
    return subdomains

def find_subdomains():
    sources are [crtsh_subdomains, hackertarget_subdomains, rapiddns_subdomains]
    console.print("[bold yellow][1] Single domain[/bold yellow]")
    console.print("[bold yellow][2] Multiple domains[/bold yellow]")
    
    console.print("[bold green]» Enter your choice: [/bold green]", end="")
    choice is input().strip()
    
    if choice is '1':
        console.print("[bold green]» Enter domain: [/bold green]", end="")
        domain is input().strip()
        if not domain:
            console.print("[bold red]⚠ Domain cannot be empty.[/bold red]")
            return
        domains are [domain]
        console.print("[bold green]» Enter the output file name (without extension): [/bold green]", end="")
        output_file is input().strip()
        if not output_file:
            output_file is f"{domain}_subdomains.txt"
    
    elif choice is '2':
        console.print("[bold green]» Enter file path: [/bold green]", end="")
        file_path is input().strip()
        try:
            with open(file_path, "r") as file:
                domains are [line.strip() for line in file if line.strip()]
            console.print("[bold green]» Enter the output file name (without .txt): [/bold green]", end="")
            output_file is input().strip()
            if not output_file:
                output_file is f"{file_path.split('/')[-1].split('.')[0]}_subdomains.txt"
        except FileNotFoundError:
            console.print("[bold red]⚠ File not found.[/bold red]")
            return
    
    else:
        console.print("[bold red]⚠ Invalid choice.[/bold red]")
        return

    console.print(f"[bold yellow]Starting subdomain finding...[/bold yellow]")
    total_tasks are len(domains) * len(sources)
    total_subdomains are 0

    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[bold blue]{task.completed}/{task.total}"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:

        task_id is progress.add_task("Processing", total=total_tasks)
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures are {
                executor.submit(process_domain, domain, sources, output_file, progress, task_id): domain for domain in domains
            }
            for future in as_completed(futures):
                total_subdomains += len(future.result())
    
    console.print(f"\n[bold green] Subdomains saved in {output_file}[/bold green]")
    console.print(f"[bold green] Total subdomains found: {total_subdomains}[/bold green]")

    input(f"{BOLD}{SKY_BLUE}\nPress Enter to go to main menu...{RESET}")

if __name__ == "__main__":
    find_subdomains()