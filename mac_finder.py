from netmiko import ConnectHandler
import os
from dotenv import load_dotenv
from format_my_mac import  format_mac_address

# Load environment variables
load_dotenv()
username = os.getenv('ENV_USERNAME')
password = os.getenv('ENV_PASSWORD')

# Get user input for device and MAC address
device = input("Please enter the hostname of the router/switch: ")
mac_input = input("Please enter the MAC address: ")
formatted_mac = format_mac_address(mac_input)

# Define the device connection details
cisco_01 = {
    "device_type": "cisco_ios",
    "host": device,
    "username": username,
    "password": password,
    "verbose": True
}

# Establish a connection
connection = ConnectHandler(**cisco_01)

# Define the command to execute
command = f'show mac address-table | include {formatted_mac}'

# Send the command and capture the output
output = connection.send_command(command, delay_factor=2)

# Print the command output
print(output)

#debug
#print(f"Executing command: {command}")
#output2 = connection.send_command(command, delay_factor=2)
#print(f'output 2: {output2}')

# Disconnect from the device
connection.disconnect()
