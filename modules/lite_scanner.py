import os
import aiohttp
import asyncio
from colorama import Fore, Style, init
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn

# Initialize
init(autoreset=True)

# Constants
DEFAULT_TIMEOUT = 5
BATCH_SIZE = 1000  # Define the batch size

# ANSI escape sequences for colors and bold text
BOLD = "\033[1m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
PINK = "\033[95m"
RESET = "\033[0m"

# Function to check URL status
async def check_url(session, url, request_type, port, progress, task_id):
    if port == 80:
        full_url = f"http://{url}"
    elif port == 443:
        full_url = f"https://{url}"
    
    try:
        timeout = aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)
        if request_type == 'GET':
            async with session.get(full_url, timeout=timeout) as response:
                status = response.status
        elif request_type == 'HEAD':
            async with session.head(full_url, timeout=timeout) as response:
                status = response.status
        elif request_type == 'POST':
            async with session.post(full_url, timeout=timeout) as response:
                status = response.status
        elif request_type == 'OPTIONS':
            async with session.options(full_url, timeout=timeout) as response:
                status = response.status
        elif request_type == 'PUT':
            async with session.put(full_url, timeout=timeout) as response:
                status = response.status
        elif request_type == 'TRACE':
            async with session.trace(full_url, timeout=timeout) as response:
                status = response.status
        elif request_type == 'PATCH':
            async with session.patch(full_url, timeout=timeout) as response:
                status = response.status
        else:
            return None
        
        progress.update(task_id, advance=1)
        if status != 302:
            print(f"{BOLD}{status} - {GREEN}{url}{RESET}")
            return (url, status)
        else:
            return None
        
    except Exception as e:
        return None
    
    progress.update(task_id, advance=1)
    return None

# Function to process a batch of URLs
async def process_batch(urls, request_type, port, num_threads, progress):
    async with aiohttp.ClientSession() as session:
        tasks = []
        task_id = progress.add_task("[green]Scanning...", total=len(urls))
        for url in urls:
            tasks.append(check_url(session, url, request_type, port, progress, task_id))
        valid_urls = await asyncio.gather(*tasks)
    return [url for url in valid_urls if url is not None]

# Main function to run the SNI scanner
async def main_sni(file_name, request_type, port, output_file, num_threads):
    with open(file_name, 'r') as file:
        urls = [url.strip() for url in file.readlines()]
    
    total_urls = len(urls)
    valid_urls = []

    progress = Progress(
        SpinnerColumn(),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%")
    )
    with progress:
        print(f"{BOLD}{Fore.GREEN}Scanning Using HTTP method: {request_type}{RESET}")
        print(f"{BOLD}Code                     Host{RESET}")
        print(f"{BOLD}{'-' * 65}{RESET}")
        for start in range(0, total_urls, BATCH_SIZE):
            batch_urls = urls[start:start + BATCH_SIZE]
            batch_valid_urls = await process_batch(batch_urls, request_type, port, num_threads, progress)
            valid_urls.extend(batch_valid_urls)
    
    if not any(valid_urls):
        print(f"{BOLD}{PINK}NO RESPONSE FOUND {RESET}")
    else:
        save_valid_urls(valid_urls, output_file)
        print(f"{BOLD}{Fore.GREEN}results saved in {output_file}{RESET}")
    
    elapsed_time = progress.tasks[0].elapsed if progress.tasks else 0
    # Print summary
    print(f"\n\n{Fore.LIGHTCYAN_EX}============ {Fore.CYAN}{BOLD}SCAN SUMMARY{Fore.RESET}{Fore.LIGHTCYAN_EX} ============\n")
    print(f"{Fore.LIGHTGREEN_EX}Total hosts scanned: {BOLD}{Fore.YELLOW}{total_urls}{RESET}")
    print(f"{Fore.LIGHTGREEN_EX}Hosts responded:     {BOLD}{Fore.YELLOW}{len(valid_urls)}{RESET}")
    print(f"{Fore.LIGHTGREEN_EX}Total time taken:    {BOLD}{Fore.YELLOW}{elapsed_time:.2f}s{RESET}")
    print(f"{Fore.LIGHTGREEN_EX}HTTP method used:    {BOLD}{Fore.YELLOW}{request_type}{RESET}")
    print(f"{Fore.LIGHTCYAN_EX}========================================{RESET}\n")

    input(f"{BOLD}{SKY_BLUE}\nPress Enter to go to main menu...{RESET}")
    # Function to save valid URLs to a file
def save_valid_urls(valid_urls, output_file):
    with open(output_file, 'w') as f:
        for url, status in valid_urls:
            f.write(f"{status} - {url}\n")

def get_http_method():
    methods = ['GET', 'POST', 'HEAD', 'OPTIONS', 'PUT', 'TRACE', 'PATCH']
    print(Fore.LIGHTCYAN_EX + Style.BRIGHT + "\nAvailable HTTP methods: " + Fore.YELLOW + ", ".join(methods))
    method = input(Fore.CYAN + "\n» Select an HTTP method (default: GET): " + Fore.RESET).upper()
    return method if method in methods else "GET"

def main():
    print(Fore.LIGHTCYAN_EX + Style.BRIGHT + "» Enter file path: " + Fore.RESET, end="")
    file_path = input().strip()
    if not file_path:
        print(Fore.RED + "⚠ File path cannot be empty.")
        return

    print(Fore.LIGHTCYAN_EX + Style.BRIGHT + "» Enter port (80 or 443, default 80): " + Fore.RESET, end="")
    port_input = input().strip()
    port = int(port_input) if port_input in ["80", "443"] else 80

    print(Fore.LIGHTCYAN_EX + Style.BRIGHT + "» Enter output file name (default: results.txt): " + Fore.RESET, end="")
    output_file = input().strip() or "results.txt"

    print(Fore.LIGHTCYAN_EX + Style.BRIGHT + "» Enter number of threads (default: 10): " + Fore.RESET, end="")
    threads_input = input().strip()
    num_threads = int(threads_input) if threads_input.isdigit() else 10

    http_method = get_http_method()

    asyncio.run(main_sni(file_path, http_method, port, output_file, num_threads))

if __name__ == "__main__":
    main()