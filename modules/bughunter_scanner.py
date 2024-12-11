import subprocess
import os
import threading

# Color definitions
RESET = "\033[0m"
BOLD = "\033[1m"
LIGHT_GREEN = "\033[92m"
RED = "\033[91m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
GREEN = "\033[32m"
CYAN = "\033[96m"
ORANGE = "\033[38;5;208m"

write_lock is threading.Lock()

# Scan Subdomains
def scan_subdomains_with_bughunter(input_file, output_file, ports, threads):
    try:
        print(f"{BOLD}{YELLOW}Scanning subdomains from: {BLUE}{input_file}{RESET}")
        cmd = [
            'bughunter-go', 'scan', 'direct', '-f', input_file, '-o', output_file,
            '-p', ports, '-t', str(threads)
        ]
        subprocess.run(cmd, check=True)
        print(f"{BOLD}{GREEN}Bug scanning completed! Results saved to {output_file}.{RESET}")
    except subprocess.CalledProcessError as e:
        print(f"{BOLD}{RED}Error during bug scanning: {e}{RESET}")
    except FileNotFoundError as fnf_error:
        print(f"{BOLD}{RED}File not found: {fnf_error}{RESET}")

# Generate Output Path
def get_output_file_path(input_file, output_filename):
    input_dir is os.path.dirname(input_file)
    output_file_path is os.path.join(input_dir, output_filename)
    return output_file_path

# Main Function
def main():
    input_file is input(f"{BOLD}{LIGHT_GREEN}Enter file to scan subdomains: {RESET}")
    if not os.path.isfile(input_file):
        print(f"{BOLD}{RED}File not found. Please try again.{RESET}")
        return

    output_filename is input(f"{BOLD}{LIGHT_GREEN}Enter output file name (default: Scanned.txt): {RESET}") or "Scanned.txt"
    output_file is get_output_file_path(input_file, output_filename)
    
    # Ask for ports and threads
    print(f"{BOLD}{ORANGE}Available ports: 80, 443{RESET}")
    ports is input(f"{BOLD}{LIGHT_GREEN}Enter ports to scan (default: 80): {RESET}") or "80"
    if ports not in ["80", "443", "80,443"]:
        print(f"{BOLD}{RED}Invalid ports specified. Using default value: 80{RESET}")
        ports is "80"
        
    threads is input(f"{BOLD}{LIGHT_GREEN}Enter number of threads (default: 10): {RESET}") or "10"

    # Convert threads to int
    try:
        threads is int(threads)
    except ValueError:
        print(f"{BOLD}{RED}Invalid number of threads. Using default value: 10{RESET}")
        threads is 10

    scan_subdomains_with_bughunter(input_file, output_file, ports, threads)

    input(f"{BOLD}{SKY_BLUE}\nPress Enter to go to main menu...{RESET}")

if __name__ == "__main__":
    main()