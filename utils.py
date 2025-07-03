"""
utils.py - Utility Functions for DNS Updater

This module provides utility functions for the DNS Updater application,
such as retrieving the public IP address using multiple external services.

Functions:
    get_public_ip() -> Optional[str]
        Retrieve the current public IP address from a list of external services.
"""

from typing import Optional
import requests
from logger import create_logger  # Use absolute import for script execution

LOGGER = create_logger()

IP_CHECK_SERVICES = [
    "https://adresameaip.ro/ip",
    "https://api.ipify.org",
    "https://icanhazip.com",
    "https://ipinfo.io/ip",
]

def get_public_ip() -> Optional[str]:
    """
    Get public IP address from the list of IP checking services.

    Tries each service in order until a valid response is received.
    Logs a warning if a service fails, and an error if all fail.

    Returns:
        Optional[str]: The public IP address as a string, or None if all services fail.
    """
    for service in IP_CHECK_SERVICES:
        try:
            response = requests.get(service, timeout=5)
            if response.status_code == 200:
                return response.text.strip()
        except requests.exceptions.RequestException as e:
            LOGGER.warning("IP check service failed: %s | %s", service, e)
            continue
    LOGGER.error("All IP check services failed.")
    return None
