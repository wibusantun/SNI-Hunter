import os
import subprocess

# Importing your modules
from modules.api_subd import find_subdomains as api_subd
from modules.bughunter_scanner import main as bughunter_scanner
from modules.ip_domain_extractor import main as ip_domain_extractor
from modules.ip_generator import main as ip_generator
from modules.lite_scanner import scan_urls_with_request_methods as lite_scanner
from modules.normal_scanner import main as normal_scanner
from modules.subfinder import main as subfinder

# Color definitions
RESET = "\033[0m"
BOLD = "\033[1m"
LIGHT_GREEN = "\033[92m"
RED = "\033[91m"
BLUE = "\033[94m"
SKY_BLUE = "\033[1;36m"
YELLOW = "\033[93m"
GREEN = "\033[32m"
PURPLE = "\033[95m"
CYAN = "\033[96m"
WHITE = "\033[97m"
ORANGE = "\033[38;5;208m"
PINK = "\033[38;5;206m"

COLORS = [LIGHT_GREEN, RED, BLUE, YELLOW, GREEN, PURPLE, CYAN, WHITE, ORANGE, PINK]

# Show Menu
def show_menu():
    menu = f"""
    {BOLD}{LIGHT_GREEN}=============================={RESET}
    {BOLD}{YELLOW}[1]{RESET} - Find Subdomain
    {BOLD}{YELLOW}  1{RESET} - Find subdomains with subfinder
    {BOLD}{YELLOW}  2{RESET} - Find subdomains with API
    {BOLD}{YELLOW}[2]{RESET} - Scan host's
    {BOLD}{YELLOW}[3]{RESET} - Lite Scanner
    {BOLD}{YELLOW}[4]{RESET} - Extract IP/Domain
    {BOLD}{YELLOW}[5]{RESET} - IP Generator
    {BOLD}{YELLOW}[6]{RESET} - Update Scripts
    {BOLD}{YELLOW}[8]{RESET} - Exit Program
    {BOLD}{LIGHT_GREEN}=============================={RESET}
    """
    print(menu)

# Show Scan Host Menu
def show_scan_host_menu():
    menu = f"""
    {BOLD}{LIGHT_GREEN}=============================={RESET}
    {BOLD}{YELLOW}[1]{RESET} - Scan host with bughunter
    {BOLD}{YELLOW}[2]{RESET} - Scan host with hostscanner
    {BOLD}{LIGHT_GREEN}=============================={RESET}
    """
    print(menu)

# Update Function
def update_scripts():
    try:
        subprocess.run(["git", "pull"], check=True)
        print(f"{BOLD}{GREEN}Scripts updated successfully!{RESET}")
    except subprocess.CalledProcessError:
        print(f"{BOLD}{RED}Failed to update scripts. Please ensure you're connected to the internet and have git installed.{RESET}")

# Main Function
def main():
    while True:
        show_menu()
        choice = input(f"{BOLD}{SKY_BLUE}Choose an option (1-8): {RESET}").strip()

        if choice == "1":
            sub_choice = input(f"{BOLD}{SKY_BLUE}Choose an option (1-2): {RESET}").strip()
            
            if sub_choice == "1":
                subfinder()
            elif sub_choice == "2":
                api_subd()
            else:
                print(f"{BOLD}{RED}Invalid option! Please select a valid option.{RESET}")
        
        elif choice == "2":
            show_scan_host_menu()
            sub_choice = input(f"{BOLD}{SKY_BLUE}Choose an option (1-2): {RESET}").strip()
            
            if sub_choice == "1":
                bughunter_scanner()
            elif sub_choice == "2":
                normal_scanner()
            else:
                print(f"{BOLD}{RED}Invalid option! Please select a valid option.{RESET}")
        
        elif choice == "3":
            lite_scanner()
        
        elif choice == "4":
            ip_domain_extractor()
        
        elif choice == "5":
            ip_generator()
        
        elif choice == "6":
            update_scripts()
        
        elif choice == "8":
            print(f"{BOLD}{GREEN}Exiting program...{RESET}")
            break
        
        else:
            print(f"{BOLD}{RED}Invalid option! Please select a valid option.{RESET}")

if __name__ == "__main__":
    main()