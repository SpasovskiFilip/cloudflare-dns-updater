"""
DNS Updater
Author: Alexandru-Ioan Plesoiu
GitHub: https://github.com/alexplesoiu
Documentation: https://github.com/alexplesoiu/dns-updater

DNS Updater is a Python-based tool that automatically updates Cloudflare DNS records
with your public IP address. If your server's IP address changes frequently or you
have a dynamic IP, this tool ensures that your domains and subdomains always point
to the correct server. It can handle multiple domains and subdomains from multiple
zones, with proxying enabled or disabled. The tool runs checks and updates every
5 minutes and includes redundancy for IP checking services.
"""

import time
import socket
import logging
import sys
import os
import json
import requests
import schedule
from varname import nameof

# Get values from Environment variables
CF_API_TOKEN = os.getenv("CF_API_TOKEN")
CF_ZONE_ID = os.getenv("CF_ZONE_ID")
DNS_RECORD_COMMENT_KEY = os.getenv("DNS_RECORD_COMMENT_KEY")
DOMAINS_FILE_PATH = os.getenv("DOMAINS_FILE_PATH")
DOMAINS = os.getenv("DOMAINS")
SCHEDULE_MINUTES = int(os.getenv("SCHEDULE_MINUTES", "5"))
TTL_ENV = os.getenv("TTL")
PROX_ENV = os.getenv("PROXIED")
TYPE = os.getenv("TYPE")
UPDATE_TYPE = os.getenv('UPDATE_TYPE')
UPDATE_PROXY = os.getenv('UPDATE_PROXY')
UPDATE_TTL = os.getenv('UPDATE_TTL')
DOMAINS_LIST = []
# Calcualte values from above variables
if DOMAINS is not None:
    DOMAINS_LIST = DOMAINS.split(',')
CF_ZONE_ID_LIST = CF_ZONE_ID.split(',')
DNS_RECORD_COMMENT_KEY_LIST = DNS_RECORD_COMMENT_KEY.split(',')
PROXIED = bool(PROX_ENV)
TTL = int(TTL_ENV or "1")

# Define API endpoints
BASE_URL = "https://api.cloudflare.com/client/v4/"

# List of IP checking services
IP_CHECK_SERVICES = [
    "https://adresameaip.ro/ip",
    "https://api.ipify.org",
    "https://icanhazip.com",
    "https://ipinfo.io/ip",
]


def create_logger(level=logging.INFO):
    """Create the logger object"""
    logger = logging.getLogger("MGE-Logs")

    # Create handlers
    console_handler = logging.StreamHandler(sys.stdout)
    file_handler = logging.FileHandler("dns_updater.log")

    console_handler.setLevel(level)
    file_handler.setLevel(logging.WARNING)

    # Create formatters and add it to handlers
    logger_format = logging.Formatter(
        "%(asctime)s | %(filename)s | %(levelname)s | %(message)s"
    )
    file_format = logging.Formatter(
        "%(asctime)s | %(filename)s(%(lineno)d) | %(levelname)s | %(message)s"
    )

    file_handler.setFormatter(file_format)
    console_handler.setFormatter(logger_format)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.setLevel(level)

    return logger


LOGGER = create_logger()


def get_dns_record(zone_id, domain_name):
    """Get current DNS record for the specified domain"""
    LOGGER.info("Fetching record for '%s'.", domain_name)
    headers = {
        "Authorization": "Bearer " + CF_API_TOKEN,
        "Content-Type": "application/json",
    }

    params = {
        "name": domain_name,
    }

    response = requests.get(
        f"{BASE_URL}zones/{zone_id}/dns_records",
        headers=headers,
        params=params,
        timeout=60,
    )

    if response.status_code == 200:
        records = response.json()["result"]

        if records:
            LOGGER.info("Successfully fetched data for '%s'.", domain_name)
            return records[0]
        LOGGER.warning(
            "Request was successful but no valid domains were found: %s",
            response.json(),
        )
    else:
        LOGGER.error(
            "Failed to fetch data for '%s'. Response: %s", domain_name, response.json()
        )

    return None


def update_dns_record_content(record, content):
    """Update the DNS record content"""
    headers = {
        "Authorization": "Bearer " + CF_API_TOKEN,
        "Content-Type": "application/json",
    }

    data = {"content": content}

    response = requests.patch(
        f"{BASE_URL}zones/{record['zone_id']}/dns_records/{record['id']}",
        json=data,
        headers=headers,
        timeout=30,
    )

    if response.status_code == 200:
        LOGGER.info(
            "DNS record updated successfully: %s (%s) -> %s",
            record["name"],
            record["type"],
            content,
        )
    else:
        LOGGER.error("Failed to update DNS record: %s", response.json())


def update_dns_record_proxy(record, proxy):
    """Update the DNS record proxy"""
    headers = {
        "Authorization": "Bearer " + CF_API_TOKEN,
        "Content-Type": "application/json",
    }

    data = {"proxied": proxy}

    response = requests.patch(
        f"{BASE_URL}zones/{record['zone_id']}/dns_records/{record['id']}",
        json=data,
        headers=headers,
        timeout=30,
    )

    if response.status_code == 200:
        LOGGER.info(
            "DNS record proxy updated successfully: %s (%s) -> %s",
            record["name"],
            record["type"],
            proxy,
        )
    else:
        LOGGER.error("Failed to update DNS record proxy: %s", response.json())


def update_dns_record_type(record, record_type):
    """Update the DNS record record_type"""
    headers = {
        "Authorization": "Bearer " + CF_API_TOKEN,
        "Content-Type": "application/json",
    }

    data = {"type": record_type}

    response = requests.patch(
        f"{BASE_URL}zones/{record['zone_id']}/dns_records/{record['id']}",
        json=data,
        headers=headers,
        timeout=30,
    )

    if response.status_code == 200:
        LOGGER.info(
            "DNS record type updated successfully: %s (%s) -> %s",
            record["name"],
            record["type"],
            record_type,
        )
    else:
        LOGGER.error("Failed to update DNS record type: %s", response.json())


def update_dns_record_ttl(record, ttl):
    """Update the DNS record ttl"""
    headers = {
        "Authorization": "Bearer " + CF_API_TOKEN,
        "Content-Type": "application/json",
    }

    data = {"ttl": ttl}

    response = requests.patch(
        f"{BASE_URL}zones/{record['zone_id']}/dns_records/{record['id']}",
        json=data,
        headers=headers,
        timeout=30,
    )

    if response.status_code == 200:
        LOGGER.info(
            "DNS record ttl updated successfully: %s (%s) -> %s",
            record["name"],
            record["type"],
            ttl,
        )
    else:
        LOGGER.error("Failed to update DNS record ttl: %s", response.json())


def read_zones_from_file(json_file_path, zone_id):
    """Loads static wishlist of domains in json format along with their metadata"""
    with open(json_file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    zones = data["zones"]
    count = 1
    for zone in zones:
        if "$" in zone["id"]:
            if str(count) in zone["id"]:
                zone["id"] = zone_id[count-1]
                count += 1
            else:
                zone["id"] = zone_id[0]

        for domain in zone["domains"]:
            domain["zone_id"] = zone["id"]

        LOGGER.info("Sucessfully read zone %s.", zone)

    return zones


def get_dns_records_by_name(zones):
    """Fetches all DNS records that were loaded from file"""
    records = []

    LOGGER.info("Trying to fetch records for %s zones.", len(zones))

    for zone in zones:
        for domain in zone["domains"]:
            record = get_dns_record(domain["zone_id"], domain["name"])

            if record is not None:
                records.append(record)

    return records


def get_dns_records_by_domain_list(domain_list, zone_id_list):
    """Fetches all DNS records that were loaded from file"""
    records = []

    LOGGER.info(
        "Trying to fetch records for %s domains from %s zones.",
        len(domain_list),
        len(zone_id_list),
    )

    for zone in zone_id_list:
        for domain in domain_list:
            record = get_dns_record(zone, domain)

            if record is not None:
                records.append(record)

    return records


def get_dns_records_by_comment(zone_id, comment_key):
    """Fetches all DNS records that contain the comment key inside of the comment"""
    LOGGER.info("Fetching DNS record with comment key: %s", comment_key)
    headers = {
        "Authorization": "Bearer " + CF_API_TOKEN,
        "Content-Type": "application/json",
    }

    params = {
        "comment.contains": comment_key,
    }

    response = requests.get(
        f"{BASE_URL}zones/{zone_id}/dns_records",
        headers=headers,
        params=params,
        timeout=60,
    )

    if response.status_code == 200:
        records = response.json()["result"]
        if records and len(records) > 0:
            LOGGER.info("Request was successful and found %s valid domains!", len(records))
            return records
        LOGGER.warning(
            "Request was successful but no valid domains were found: %s",
            response.json(),
        )
        return []

    LOGGER.error(
        "Failed to get records! | HTTP response: %s | Error code: %s | Error message: %s",
        response.status_code,
        response.json()['errors'][0]['code'],
        response.json()['errors'][0]['message'],
    )

    return []

def get_dns_records_by_comments(zone_id_list, comment_key_list):
    """Fetches all DNS records that contain the specified comment keys 
    inside of the comment from all specified zones"""
    LOGGER.info(
        "Fetching DNS record with comment keys: %s, from %s zone(s)",
        comment_key_list,
        len(zone_id_list),
    )
    result = []
    for zone_id in zone_id_list:
        for comment_key in comment_key_list:
            records = get_dns_records_by_comment(zone_id, comment_key)
            if records and len(records) > 0:
                result.append(records)
    if result and len(result) > 0:
        return result
    LOGGER.warning("Request was successful but no valid domains were found!")
    return []


def get_public_ip():
    """Get public IP address from the list of IP checking services"""
    for service in IP_CHECK_SERVICES:
        try:
            response = requests.get(service, timeout=5)
            if response.status_code == 200:
                return response.text.strip()
        except requests.exceptions.RequestException:
            continue
    return None


def is_connected():
    """Check if there is an active internet connection"""
    try:
        host = socket.gethostbyname("www.cloudflare.com")
        socket.create_connection((host, 80), 2)
        return True
    except socket.error as exc:
        LOGGER.error("Socket error: %s", exc)
    return False


def get_all_dns_records():
    """Function to get the DNS recordsfrom a file or by zone"""
    domain_records = []

    if DNS_RECORD_COMMENT_KEY is not None:
        LOGGER.info(
            "Using DNS_RECORD_COMMENT_KEY='%s' to find DNS records to update.",
            DNS_RECORD_COMMENT_KEY,
        )
        domains_list = get_dns_records_by_comments(CF_ZONE_ID_LIST, DNS_RECORD_COMMENT_KEY_LIST)
        for list_item in domains_list:
            domain_records += list_item
    if DOMAINS is not None:
        LOGGER.info(
            "Using list of DOMAINS=[%s] to find DNS records to update.",
            DOMAINS,
        )
        domain_records = get_dns_records_by_domain_list(DOMAINS_LIST, CF_ZONE_ID_LIST)
    else:
        LOGGER.info(
            "Using DOMAINS_FILE_PATH='%s' to find DNS records to update.",
            DOMAINS_FILE_PATH,
        )
        domain_records = get_dns_records_by_name(
            read_zones_from_file(DOMAINS_FILE_PATH, CF_ZONE_ID_LIST)
        )
    return domain_records


def check_and_update_dns_record_type(record, domain_name):
    """Function to check the TYPE env variable and update the domain type"""
    if TYPE is not None:
        if TYPE != record["type"] and TYPE in ["A", "AAAA", "CNAME"]:
            update_dns_record_type(record, TYPE)
        if TYPE not in ["A", "AAAA", "CNAME"] and PROXIED is True:
            LOGGER.info(
                "Type settings are the same for %s. No update needed.",
                domain_name,
            )
        else:
            LOGGER.info(
                "Type settings are the same for %s. No update needed.",
                domain_name,
            )
    else:
        LOGGER.error(
            "Environment variable %s is not defined.", nameof(TYPE)
        )


def check_and_update_dns_record_proxy(record, domain_name):
    """Function to check the PROXIED env variable and update the domain proxy"""
    if PROX_ENV is not None:
        if record["proxiable"] is True and PROXIED != record["proxied"]:
            update_dns_record_proxy(record, PROXIED)
        else:
            if record["proxiable"] is False and PROXIED is True:
                LOGGER.error(
                    "Domain %s is not proxiable.", domain_name
                )
            if record["proxiable"] is True and PROXIED == record["proxied"]:
                LOGGER.info(
                    "Proxy settings are the same for %s. No update needed.", domain_name
                )
    else:
        LOGGER.error(
            "Environment variable %s is not defined.", nameof(PROXIED)
        )


def check_and_update_dns_record_ttl(record, domain_name):
    """Function to check the TTL env variable and update the domain ttl"""
    if TTL_ENV is not None:
        if TTL != record["ttl"] and PROXIED is False and PROX_ENV is not None:
            update_dns_record_ttl(record, TTL)
        else:
            if PROXIED is True:
                LOGGER.info(
                    "TTL settings cannot be set for %s. Proxy status is set to True.",
                    domain_name,
                )
            if TTL == record["ttl"]:
                LOGGER.info(
                    "TTL settings are the same for %s. No update needed.",
                    domain_name,
                )
    else:
        LOGGER.error(
            "Environment variable %s is not defined.", nameof(TTL)
        )

def check_connectivity():
    """Check if app is connectable to CF and if all needed variables are present"""
    if not is_connected():
        LOGGER.error("No internet connection. Skipping check and update.")
        return False

    if CF_ZONE_ID is None:
        LOGGER.error("CF_ZONE_ID: At least one zone id must be set.")
        return False
    if CF_API_TOKEN is None:
        LOGGER.error(
            "CF_API_TOKEN Missing: You have to provide your Cloudflare API Token."
        )
        return False
    if DNS_RECORD_COMMENT_KEY is None and DOMAINS_FILE_PATH is None:
        LOGGER.error(
            "DNS_RECORD_COMMENT_KEY and DOMAINS_FILE_PATH are missing,"
            + " don't know which domains to update"
        )
        return False
    return True


def check_and_update_dns():
    """Function to run the check and update process"""
    LOGGER.info("Run triggered by schedule.")

    if check_connectivity() is False:
        return

    public_ip = get_public_ip()
    domain_records = get_all_dns_records()

    valid_domains = [x["name"] for x in domain_records if x is not None]
    LOGGER.info(
        "Found %s valid domains for update: [%s]",
        len(valid_domains),
        ", ".join(valid_domains),
    )

    if public_ip:
        for record in domain_records:
            domain_name = record["name"]

            if record is None:
                LOGGER.error("DNS record for %s not found.", domain_name)
                continue

            if public_ip != record["content"]:
                update_dns_record_content(record, public_ip)
            else:
                LOGGER.info(
                    "IP addresses are the same for %s. No update needed.", domain_name
                )

            if UPDATE_TYPE is not None:
                check_and_update_dns_record_type(record, domain_name)
            if UPDATE_PROXY is not None:
                check_and_update_dns_record_proxy(record, domain_name)
            if UPDATE_TTL is not None:
                check_and_update_dns_record_ttl(record, domain_name)

    else:
        LOGGER.error("Failed to retrieve public IP. Skipping check and update.")


LOGGER.info("Schedule is set at %s minutes", SCHEDULE_MINUTES)

# Schedule the check and update process to run every X minutes
schedule.every(SCHEDULE_MINUTES).minutes.do(check_and_update_dns).run()

# Main loop
while True:
    schedule.run_pending()
    time.sleep(1)
