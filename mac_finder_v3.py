"""
Description: mac finder, the user inputs the mac address in any format and the script finds where  the device is located
Version: 3, 20241231
Author: Theo
"""

from netmiko import ConnectHandler
import os
from dotenv import load_dotenv
import re
from format_my_mac import format_mac_address
from concurrent.futures import ThreadPoolExecutor
import time

# Load environment variables
load_dotenv()
username = os.getenv('ENV_USERNAME')
password = os.getenv('ENV_PASSWORD')

# Define the function for processing a single device
def process_device(device, mac_input, visited_devices):
    formatted_mac = format_mac_address(mac_input)

    # Skip already visited devices to prevent cycles
    if device in visited_devices:
        print(f"Device {device} already visited. Skipping.")
        return None

    visited_devices.add(device)  # Mark the device as visited

    # Define the device connection details
    cisco_device = {
        "device_type": "cisco_ios",
        "host": device,
        "username": username,
        "password": password,
        "verbose": True
    }

    try:
        # Establish a connection
        connection = ConnectHandler(**cisco_device)

        # Define the command to search for the MAC address
        command = f'show mac address-table | include {formatted_mac}'
        output = connection.send_command(command, delay_factor=2)
        print(f"Searching on {device}:\n{output}")

        # Process the output to find the port
        lines = output.splitlines()
        for line in lines:
            match = re.search(r'(Gi|Po)[0-9/]+', line)
            if match:
                port = match.group(0)  # Capture the port

                if port.startswith('Gi'):
                    print(f"MAC Address found on port: {port} of device {device}")
                    connection.disconnect()
                    return None  # Stop recursion

                elif port.startswith('Po'):
                    print(f"MAC Address is on another switch via port: {port}")

                    # Get interface details to find the next switch hostname
                    interface_command = f'show run int {port}'
                    interface_output = connection.send_command(interface_command, delay_factor=2)

                    # Search for the line with "description" and extract the hostname
                    description_match = re.search(r'description.*\b(ch\w+)', interface_output, re.IGNORECASE)
                    if description_match:
                        next_device = description_match.group(1)
                        print(f"Next switch to SSH into: {next_device}")
                        connection.disconnect()
                        return next_device  # Return the next device to connect to

        print(f"No matching port found on {device}.")
    except Exception as e:
        print(f"Error connecting to {device}: {e}")
    finally:
        connection.disconnect()

    return None  # No further device to connect to

# Define the recursive function with parallel threading
def find_mac_address_parallel(initial_device, mac_input):
    visited_devices = set()  # Keep track of visited devices to avoid cycles
    next_devices = [initial_device]

    with ThreadPoolExecutor(max_workers=5) as executor:
        while next_devices:
            # Dispatch tasks for each device in the next_devices list
            futures = {
                executor.submit(process_device, device, mac_input, visited_devices): device
                for device in next_devices
            }

            next_devices = []  # Reset the list of next devices

            for future in futures:
                try:
                    result = future.result()
                    if result:  # If a next device is found, add it to the list
                        next_devices.append(result)
                except Exception as e:
                    print(f"Error processing a device: {e}")

# Get initial user input
initial_device = input("Please enter the hostname of the initial router/switch: ")
mac_address = input("Please enter the MAC address: ")

# Measure start time
start_time = time.time()

# Start the search
find_mac_address_parallel(initial_device, mac_address)

# Measure end time
end_time = time.time()

# Calculate and print the elapsed time
elapsed_time = end_time - start_time
print(f"\nScript execution time: {elapsed_time:.2f} seconds")

