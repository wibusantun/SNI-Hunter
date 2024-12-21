import os
import re
from colorama import Fore, Style, init
import time

init(autoreset=True)

BOLD = "\033[1m"
SKY_BLUE = "\033[94m"
RESET = "\033[0m"

def solicit_input(message):
    return input(f"{Fore.GREEN + Style.BRIGHT}{message}{Style.RESET_ALL}").strip()

def process_text(file_location, destination):
    try:
        with open(file_location, 'r') as source:
            lines = source.readlines()
    except (FileNotFoundError, PermissionError) as error:
        print(Fore.RED + f"Access Issue: {error}")
        return
    except Exception as error:
        print(Fore.RED + f"Unexpected Error: {error}")
        return

    total = len(lines)
    domain_regex = re.compile(r'\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b')
    
    # Updated IP regex (no capturing groups)
    ip_regex = re.compile(
        r'\b(?:25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.'
        r'(?:25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.'
        r'(?:25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.'
        r'(?:25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\b'
    )

    domain_set, ip_set = set(), set()

    for index, content in enumerate(lines):
        domain_set.update(domain_regex.findall(content))
        ip_set.update(ip_regex.findall(content))  # Now returns plain strings
        progress_bar(index + 1, total)

    if not (domain_set or ip_set):
        print(Fore.YELLOW + "No discernible data identified.")
        return

    save_location = '/storage/emulated/0/'
    final_path = os.path.join(save_location, destination)

    try:
        with open(final_path, 'w') as target:
            target.write('\n'.join(sorted(domain_set)) + "\n\n\n\n")
            target.write('\n'.join(sorted(ip_set)) + "\n")  # Tuple issue resolved
    except Exception as error:
        print(Fore.RED + f"Write Error: {error}")
        return

    print(Fore.GREEN + f"Results stored at: {final_path}\n")

def progress_bar(current, total):
    bar_length = 20
    filled = int(bar_length * current // total)
    print(f"[{'*' * filled}{' ' * (bar_length - filled)}] {int((current / total) * 100)}%", end='\r')

def render_banner(text):
    try:
        width = os.get_terminal_size().columns
    except OSError:
        width = 80
    text = text[:width - 4] if len(text) > width - 4 else text
    padding = (width - len(text) - 2) // 2
    return f"{'=' * width}\n|{' ' * padding}{text}{' ' * (padding - 1)}|\n{'=' * width}\n"

def orchestrate():
    print(Fore.CYAN + Style.BRIGHT + render_banner("IP and Domain Analyzer") + Style.RESET_ALL)
    file_location = solicit_input("Specify path to the text file: ")
    
    if not os.path.exists(file_location) or not file_location.lower().endswith('.txt'):
        print(Fore.RED + "Invalid or non-existent file. Ensure path correctness and format compliance.")
        return
    
    output_name = solicit_input("Define the output file name (default: result.txt): ")
    output_name = output_name if output_name.endswith('.txt') else f"{output_name}.txt"

    process_text(file_location, output_name)
    solicit_input("Press Enter to continue...")

if __name__ == "__main__":
    orchestrate()
