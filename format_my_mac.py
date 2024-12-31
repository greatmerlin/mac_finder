"""
Description: format a mac address to xxxx.xxxx.xxxx
Version: 1.1
Author: Theo
"""

import re

def format_mac_address(mac):
    """
    Format a MAC address into xxxx.xxxx.xxxx format (lowercase).
    """
    # Clean the MAC address by removing any non-hexadecimal characters
    cleaned_mac = re.sub(r"[^a-fA-F0-9]", "", mac)

    # Validate the length of the cleaned MAC address
    if len(cleaned_mac) != 12:
        raise ValueError("Invalid MAC address length!")
    
    # Format the MAC address as xxxx.xxxx.xxxx
    formatted_mac = ".".join(cleaned_mac[i:i+4].lower() for i in range(0, 12, 4))
    return formatted_mac

