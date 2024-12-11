import ipaddress
from tqdm import tqdm
import logging
import os

# Setup logging configuration
logging.basicConfig(filename='ip_generator.log', level=logging.DEBUG, format='%(asctime)s - %(message)s')

def log_event(message):
    logging.info(message)

def save_ips_to_file(ip_list, file_name):
    try:
        with open(file_name, "w") as f:
            for ip in ip_list:
                f.write(f"{ip}\n")
        print(f"\033[1;32mIPs successfully saved to {file_name}\033[0m")
        log_event(f"IPs successfully saved to {file_name}")
    except FileNotFoundError:
        print(f"\033[1;31mError: The specified file path does not exist!\033[0m")
    except IOError as e:
        print(f"\033[1;31mError: Unable to write to file. {e}\033[0m")
    except Exception as e:
        print(f"\033[1;31mUnexpected error occurred: {e}\033[0m")
        log_event(f"Error: {e}")

def is_valid_ip(ip):
    try:
        ipaddress.IPv4Address(ip)
        return True
    except ValueError:
        return False

def is_valid_cidr(cidr):
    try:
        ipaddress.ip_network(cidr, strict=False)
        return True
    except ValueError:
        return False

def get_valid_ip(prompt):
    while True:
        ip = input(prompt)
        if is_valid_ip(ip):
            return ip
        else:
            print("\033[1;31mInvalid IP address. Please enter a valid IP address.\033[0m")

def generate_ips_from_cidr(cidr, file_name):
    try:
        network = ipaddress.ip_network(cidr, strict=False)
        ip_list = list(network.hosts())
        total_ips = len(ip_list)
        print(f"\033[1;34mGenerating IPs for CIDR: {cidr}\033[0m")

        with tqdm(total=total_ips, desc="Progress", ncols=75) as pbar:
            save_ips_to_file(ip_list, file_name)
            pbar.update(total_ips)
    except ValueError:
        print(f"\033[1;31mError: Invalid CIDR range '{cidr}'. Please check the format!\033[0m")
    except Exception as e:
        print(f"\033[1;31mUnexpected error occurred: {e}\033[0m")
        log_event(f"Error: {e}")

def generate_ips_from_range(start_ip, end_ip, file_name):
    try:
        start = ipaddress.IPv4Address(start_ip)
        end = ipaddress.IPv4Address(end_ip)

        if start > end:
            print("\033[1;31mError: Starting IP must be less than or equal to the Ending IP!\033[0m")
            return

        ip_list = [ipaddress.IPv4Address(ip) for ip in range(int(start), int(end) + 1)]
        total_ips = len(ip_list)
        print(f"\033[1;34mGenerating IPs from {start_ip} to {end_ip}\033[0m")

        with tqdm(total=total_ips, desc="Progress", ncols=75) as pbar:
            save_ips_to_file(ip_list, file_name)
            pbar.update(total_ips)
    except ValueError:
        print(f"\033[1;31mError: Invalid IP address range '{start_ip} - {end_ip}'.\033[0m")
    except Exception as e:
        print(f"\033[1;31mUnexpected error occurred: {e}\033[0m")
        log_event(f"Error: {e}")

def parse_file_for_cidr(file_name, output_file):
    try:
        with open(file_name, "r") as f:
            lines = f.readlines()

        cidr_ranges = [line.strip() for line in lines if "/" in line]
        if not cidr_ranges:
            print(f"\033