import os
from pathlib import Path
import socket
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import Fore, Style, init
import requests
import random

# Initialize colorama
init(autoreset=True)

DEFAULT_TIMEOUT1 = 5
EXCLUDE_LOCATIONS = ["https://jio.com/BalanceExhaust", "http://filter.ncell.com.np/nc"]
file_write_lock = threading.Lock()

BANNER_TEXT = r"""
╭━╮╱╭╮╱╱╱╱╱╱╱╱╱╱╭╮╭━━━╮
┃┃╰╮┃┃╱╱╱╱╱╱╱╱╱╱┃┃┃╭━╮┃
┃╭╮╰╯┣━━┳━┳╮╭┳━━┫┃┃╰━━┳━━┳━━┳━╮╭━╮╭━━┳━╮
┃┃╰╮┃┃╭╮┃╭┫╰╯┃╭╮┃┃╰━━╮┃╭━┫╭╮┃╭╮┫╭╮┫┃━┫╭╯
┃┃╱┃┃┃╰╯┃┃┃┃┃┃╭╮┃╰┫╰━╯┃╰━┫╭╮┃┃┃┃┃┃┃┃━┫┃
╰╯╱╰━┻━━┻╯╰┻┻┻╯╰┻━┻━━━┻━━┻╯╰┻╯╰┻╯╰┻━━┻╯
"""
BANNER_COLORS = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN]

# Clear the terminal screen and display a random-colored banner
def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")
    banner_color = random.choice(BANNER_COLORS)
    print(banner_color + Style.BRIGHT + BANNER_TEXT + Style.RESET_ALL)

# Input with retry for compulsory fields
def get_compulsory_input(prompt, max_attempts=3):
    attempts = 0
    while attempts < max_attempts:
        user_input = input(prompt).strip()
        if user_input:
            return user_input
        else:
            print(Fore.RED + f"⚠ Invalid input. Attempts left: {max_attempts - attempts - 1}")
            attempts += 1
    print(Fore.RED + "⚠ Too many invalid attempts. Returning to main menu...\n")
    return None

# Input with optional defaults
def get_optional_input(prompt, default=None):
    user_input = input(prompt).strip()
    return user_input if user_input else default

# Read hosts from file
def get_hosts_from_file(file_path):
    path = Path(file_path)
    if path.is_file():
        try:
            return [line.strip() for line in path.read_text().splitlines() if line.strip()]
        except Exception as e:
            print(Fore.RED + f"Error reading file: {e}")
    return []

# Choose HTTP method
def get_http_method():
    methods = ['GET', 'POST', 'HEAD']
    print(Fore.LIGHTCYAN_EX + Style.BRIGHT + "\nAvailable HTTP methods: " + Fore.YELLOW + ", ".join(methods))
    method = get_optional_input(Fore.CYAN + "\n » Select an HTTP method (default: GET): " + Fore.RESET, "GET").upper()
    return method if method in methods else "GET"

# Format elapsed time
def format_time(elapsed_time):
    return f"{int(elapsed_time // 60)}m {int(elapsed_time % 60)}s" if elapsed_time >= 60 else f"{elapsed_time:.2f}s"

# Format the row for console and file output
def format_row(code, server, port, ip_address, host, use_colors=True):
    return (f"{Style.BRIGHT + Fore.GREEN if use_colors else ''}{code:<4} " +
            f"{Style.BRIGHT + Fore.CYAN if use_colors else ''}{server:<20} " +
            f"{Style.BRIGHT + Fore.YELLOW if use_colors else ''}{port:<5} " +
            f"{Style.BRIGHT + Fore.MAGENTA if use_colors else ''}{ip_address:<15} " +
            f"{Style.BRIGHT + Fore.LIGHTBLUE_EX if use_colors else ''}{host}{Style.RESET_ALL if use_colors else ''}")
            
          # Check HTTP response
def check_http_response(host, port, method):
    url = f"{'https' if port in ['443', '8443'] else 'http'}://{host}:{port}"
    try:
        response = requests.request(method, url, timeout=DEFAULT_TIMEOUT1, allow_redirects=True)
        if any(exclude in response.headers.get('Location', '') for exclude in EXCLUDE_LOCATIONS):
            return None
        status_code = response.status_code
        server_header = response.headers.get('Server', 'N/A')
        ip_address = get_ip_from_host(host) or 'N/A'
        return (status_code, server_header, port, ip_address, host)
    except requests.exceptions.RequestException:
        return None

# Resolve IP address from hostname
def get_ip_from_host(host):
    try:
        return socket.gethostbyname(host)
    except socket.gaierror:
        return "N/A"

# Perform scan
def perform_scan(hosts, ports, output_file, threads, method):
    clear_screen()
    print(Fore.GREEN + Style.BRIGHT + "🔍 Scanning Using HTTP method:", Fore.YELLOW + method)
    
    headers = (Fore.GREEN + Style.BRIGHT + "Code  " + Fore.CYAN + "Server               " +
              Fore.YELLOW + "Port   " + Fore.MAGENTA + "IP Address     " + Fore.LIGHTBLUE_EX + "Host" + Style.RESET_ALL)
    separator = "-" * 65

    output_path = Path(f"/storage/emulated/0/{output_file}")
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'a') as file:
            file.write(f"{headers}\n{separator}\n")
    except Exception as e:
        print(Fore.RED + f"Error opening output file: {e}")
        return

    print(headers, separator, sep='\n')
    start_time = time.time()
    total_hosts, scanned_hosts, responded_hosts = len(hosts) * len(ports), 0, 0

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [executor.submit(check_http_response, host, port, method) for host in hosts for port in ports]
        for future in as_completed(futures):
            scanned_hosts += 1
            try:
                result = future.result(timeout=DEFAULT_TIMEOUT1 + 1)
                if result:
                    responded_hosts += 1
                    row = format_row(*result)
                    print(Style.BRIGHT + row)
                    with file_write_lock:
                        with open(output_path, 'a') as file:
                            file.write(format_row(*result, use_colors=False) + "\n")
            except Exception:
                pass

    elapsed_time = time.time() - start_time
    print(f"\n\n{Fore.GREEN}✔ Scan completed! {responded_hosts}/{scanned_hosts} hosts responded.")
    print(f"{Fore.GREEN}Results saved to {output_path}.{Style.RESET_ALL}")
    
# Main function
def main():
    while True:
        clear_screen()
        file_path = get_compulsory_input(Fore.GREEN + "» Enter file path: " + Fore.YELLOW)
        if not file_path:
            return

        hosts = get_hosts_from_file(file_path)
        if not hosts:
            print(Fore.RED + "⚠ No valid hosts found in the file.")
            continue

        ports_input = get_optional_input(Fore.GREEN + "» Enter port list (default: 80): " + Fore.YELLOW, "80")
        ports = [port.strip() for port in ports_input.split(',') if port.strip().isdigit()]
        ports = ports if ports else ["80"]

        output_file = get_optional_input(Fore.GREEN + "» Enter output file name (default: scan_results.txt): " + Fore.YELLOW, "scan_results.txt")
        threads_input = get_optional_input(Fore.GREEN + "» Enter number of threads (default: 10): " + Fore.YELLOW, "10")
        threads = int(threads_input) if threads_input.isdigit() else 10

        method = get_http_method()
        perform_scan(hosts, ports, output_file, threads, method)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Fore.RED + "\nProgram interrupted by user. Exiting...")