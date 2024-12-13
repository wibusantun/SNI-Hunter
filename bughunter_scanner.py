import subprocess
import os
import threading
from pathlib import Path

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
SKY_BLUE = "\033[1;36m"

write_lock = threading.Lock()

# Check if 'bughunter-go' binary exists and is in PATH
def check_bughunter_installed():
    try:
        subprocess.run(['bughunter-go', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        print(f"{BOLD}{RED}Error: 'bughunter-go' binary is not installed or not found in the system PATH.{RESET}")
        return False
    except subprocess.CalledProcessError:
        print(f"{BOLD}{RED}Error: 'bughunter-go' binary execution failed. Please check the installation.{RESET}")
        return False
    return True

# Scan Subdomains with Bughunter
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
        print(f"{BOLD}{RED}Error: {fnf_error}. Please ensure the 'bughunter-go' binary is installed and accessible.{RESET}")
    except Exception as ex:
        print(f"{BOLD}{RED}An unexpected error occurred: {ex}{RESET}")

# Generate Output Path
def get_output_file_path(input_file, output_filename):
    input_dir = os.path.dirname(input_file)
    output_file_path = Path(input_dir) / output_filename  # Correct path joining with Path
    return output_file_path

# Validate File Path
def validate_file(input_file):
    if not os.path.isfile(input_file):
        print(f"{BOLD}{RED}File not found: {input_file}. Please check the path and try again.{RESET}")
        return False
    return True

# Validate Ports Input (supporting any port format now)
def validate_ports(ports):
    # Allow any comma-separated list of ports
    valid_ports = [p.strip() for p in ports.split(',')]
    for port in valid_ports:
        if not port.isdigit() or int(port) not in range(1, 65536):  # Validating range of ports
            print(f"{BOLD}{RED}Invalid port {port}. Using default value: 80{RESET}")
            return "80"
    return ','.join(valid_ports)

# Validate Thread Input
def validate_threads(threads):
    try:
        threads = int(threads)
        if threads <= 0:
            print(f"{BOLD}{RED}Invalid number of threads. Using default value: 10{RESET}")
            return 10
        return threads
    except ValueError:
        print(f"{BOLD}{RED}Invalid input for threads. Using default value: 10{RESET}")
        return 10

# Main Function
def main():
    # Check if BugHunter is installed
    if not check_bughunter_installed():
        return
    
    # Ask for input file to scan
    input_file = input(f"{BOLD}{LIGHT_GREEN}Enter file to scan subdomains: {RESET}")
    
    # Validate if the file exists
    if not validate_file(input_file):
        return

    # Get output filename, default to "Scanned.txt"
    output_filename = input(f"{BOLD}{LIGHT_GREEN}Enter output file name (default: Scanned.txt): {RESET}") or "Scanned.txt"
    
    # Get the output file path
    output_file = get_output_file_path(input_file, output_filename)

    # Ask for ports and threads for scanning
    print(f"{BOLD}{ORANGE}Available ports: 80, 443, or any comma-separated list of ports (e.g., 80,443){RESET}")
    ports = input(f"{BOLD}{LIGHT_GREEN}Enter ports to scan (default: 80): {RESET}") or "80"
    
    # Validate ports
    ports = validate_ports(ports)
    
    # Ask for number of threads to use
    threads = input(f"{BOLD}{LIGHT_GREEN}Enter number of threads (default: 10): {RESET}") or "10"
    
    # Validate threads
    threads = validate_threads(threads)

    # Call the function to start the scanning process
    scan_subdomains_with_bughunter(input_file, output_file, ports, threads)

    # Wait for the user to press Enter before going to the main menu
    input(f"{BOLD}{SKY_BLUE}\nPress Enter to go to the main menu...{RESET}")

# Run the program synchronously
if __name__ == "__main__":
    main()