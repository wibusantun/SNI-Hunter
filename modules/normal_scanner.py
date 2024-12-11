import aiohttp
import asyncio
from aiohttp import ClientTimeout
import os
from colorama import Fore, Style, init
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn

init(autoreset=True)

# Color definitions
BOLD = "\033[1m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
PINK = "\033[95m"
RESET = "\033[0m"

# Function to scan a URL using a specific HTTP method
async def scan_url(session, url, request_type, timeout, progress, task_id):
    try:
        if request_type == 'GET':
            async with session.get(url, timeout=timeout) as response:
                status = response.status
        elif request_type == 'POST':
            async with session.post(url, timeout=timeout) as response:
                status = response.status
        elif request_type == 'HEAD':
            async with session.head(url, timeout=timeout) as response:
                status = response.status
        elif request_type == 'OPTIONS':
            async with session.options(url, timeout=timeout) as response:
                status = response.status
        elif request_type == 'PUT':
            async with session.put(url, timeout=timeout) as response:
                status = response.status
        elif request_type == 'TRACE':
            async with session.trace(url, timeout=timeout) as response:
                status = response.status
        elif request_type == 'PATCH':
            async with session.patch(url, timeout=timeout) as response:
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

# Function to process a batch of URLs
async def process_batch(session, urls, request_type, timeout, progress, task_id):
    tasks = []
    for url in urls:
        tasks.append(scan_url(session, url, request_type, timeout, progress, task_id))
    return await asyncio.gather(*tasks)

# Main function to run the scanner
async def main_scanner(file_name, request_type, output_file, timeout, num_threads):
    async with aiohttp.ClientSession() as session:
        with open(file_name, 'r') as file:
            urls = [url.strip() for url in file.readlines()]

        total_urls = len(urls)
        valid_urls = []

        progress = Progress(
            SpinnerColumn(),
            BarColumn(),
            TextColumn("[progress.description]{task.description}"),
            TextColumn("[progress.percentage]{task.completed}/{task.total}"),
        )

        with progress:
            task_id = progress.add_task("Scanning...", total=total_urls)
            for i in range(0, total_urls, num_threads):
                batch_urls = urls[i:i + num_threads]
                results = await process_batch(session, batch_urls, request_type, timeout, progress, task_id)
                valid_urls.extend([res for res in results if res is not None])

        if not valid_urls:
            print(f"{BOLD}{PINK}NO RESPONSE FOUND {RESET}")
        else:
            save_valid_urls(valid_urls, output_file)
            print(f"{BOLD}{Fore.GREEN}Results saved in {output_file}{RESET}")

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

    print(Fore.LIGHTCYAN_EX + Style.BRIGHT + "» Enter output file name (default: results.txt): " + Fore.RESET, end="")
    output_file = input().strip() or "results.txt"

    print(Fore.LIGHTCYAN_EX + Style.BRIGHT + "» Enter number of threads (default: 10): " + Fore.RESET, end="")
    threads_input = input().strip()
    num_threads = int(threads_input) if threads_input.isdigit() else 10

    http_method = get_http_method()
    
    timeout = ClientTimeout(total=10)

    asyncio.run(main_scanner(file_path, http_method, output_file, timeout, num_threads))

if __name__ == "__main__":
    main()