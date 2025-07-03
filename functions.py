"""
functions.py - Core Logic for DNS Updater
DNS Updater
Original Author: Alexandru-Ioan Plesoiu
Contributor: Filip Spasovski
Original GitHub: https://github.com/SpasovskiFilip
Contributor GitHub: 
Documentation: https://github.com/SpasovskiFilip/dns-updater

Defining functions for execution

This module contains the main logic for interacting with the Cloudflare API, managing DNS
records, and orchestrating the update process for dynamic DNS.

Functions:
    get_dns_record(zone_id, domain_name)
    update_dns_record_content(record, content)
    update_dns_record_proxy(record, proxy)
    update_dns_record_type(record, record_type)
    update_dns_record_ttl(record, ttl)
    read_zones_from_file(json_file_path, zone_id)
    get_dns_records_by_name(zones)
    get_dns_records_by_domain_list(domain_list, zone_id_list)
    get_dns_records_by_comment(zone_id, comment_key)
    get_dns_records_by_comments(zone_id_list, comment_key_list)
    is_connected()
    get_all_dns_records()
    check_and_update_dns_record_type(record, domain_name)
    check_and_update_dns_record_proxy(record, domain_name)
    check_and_update_dns_record_ttl(record, domain_name)
    check_connectivity()
    check_and_update_dns()

Each function includes a detailed docstring describing its purpose, 
arguments, and return value.
"""

import socket
import json
from typing import List
import requests
from logger import create_logger
from config import get_env_var
from utils import get_public_ip

CF_API_TOKEN = get_env_var("CF_API_TOKEN", required=True)
CF_ZONE_ID = get_env_var("CF_ZONE_ID", required=True)
DNS_RECORD_COMMENT_KEY = get_env_var("DNS_RECORD_COMMENT_KEY")
DOMAINS_FILE_PATH = get_env_var("DOMAINS_FILE_PATH")
DOMAINS = get_env_var("DOMAINS")
SCHEDULE_MINUTES = int(get_env_var("SCHEDULE_MINUTES", 5))
TTL_ENV = get_env_var("TTL")
PROX_ENV = get_env_var("PROXIED")
TYPE = get_env_var("TYPE")
UPDATE_TYPE = get_env_var('UPDATE_TYPE', False)
UPDATE_PROXY = get_env_var('UPDATE_PROXY', False)
UPDATE_TTL = get_env_var('UPDATE_TTL', False)

DOMAINS_LIST: List[str] = []
CF_ZONE_ID_LIST: List[str] = []
DNS_RECORD_COMMENT_KEY_LIST: List[str] = []

if DOMAINS is not None:
    DOMAINS_LIST = [d.strip() for d in DOMAINS.split(',') if d.strip()]
if CF_ZONE_ID is not None:
    CF_ZONE_ID_LIST = [z.strip() for z in CF_ZONE_ID.split(',') if z.strip()]
if DNS_RECORD_COMMENT_KEY is not None:
    DRCK = DNS_RECORD_COMMENT_KEY.split(',')
    DNS_RECORD_COMMENT_KEY_LIST = [c.strip() for c in DRCK if c.strip()]
PROXIED = PROX_ENV == 'True'
TTL = int(TTL_ENV or "1")

# Define API endpoints
BASE_URL = "https://api.cloudflare.com/client/v4/"

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
            record = records[0]
            # Attach zone_id to the record for downstream use
            record["zone_id"] = zone_id
            return record
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
                record["zone_id"] = domain["zone_id"]  # Ensure zone_id is set
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
                record["zone_id"] = zone  # Ensure zone_id is set
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
            for record in records:
                record["zone_id"] = zone_id  # Ensure zone_id is set
                LOGGER.info("Type: %s | Content: %s | Comment: %s | Name: %s",
                            record["type"], record["content"], record["comment"], record["name"])
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
                for record in records:
                    record["zone_id"] = zone_id  # Ensure zone_id is set
                result.append(records)
    if result and len(result) > 0:
        return [item for sublist in result for item in sublist]  # flatten
    LOGGER.warning("Request was successful but no valid domains were found!")
    return []


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
        domain_records = get_dns_records_by_comments(CF_ZONE_ID_LIST, DNS_RECORD_COMMENT_KEY_LIST)
        return domain_records
    if DOMAINS is not None:
        LOGGER.info(
            "Using list of DOMAINS=[%s] to find DNS records to update.",
            DOMAINS,
        )
        domain_records = get_dns_records_by_domain_list(DOMAINS_LIST, CF_ZONE_ID_LIST)
        return domain_records
    if DOMAINS_FILE_PATH is not None:
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
            "Environment variable TYPE is not defined.")


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
            "Environment variable PROXIED is not defined.")


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
            "Environment variable TTL is not defined.")


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
    if DNS_RECORD_COMMENT_KEY is None and DOMAINS_FILE_PATH is None and DOMAINS is None:
        LOGGER.error(
            "DNS_RECORD_COMMENT_KEY and DOMAINS_FILE_PATH and DOMAINS are missing,"
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
    # public_ip = "xx.xxx.xxx.xx"  # For testing purposes
    domain_records = get_all_dns_records()

    # Only include dicts with a 'name' key
    valid_domains = [x["name"] for x in domain_records if x is not None]
    LOGGER.info(
        "Found %s valid domains for update: [%s]",
        len(valid_domains),
        ", ".join(valid_domains),
    )

    if public_ip:
        LOGGER.info("Public IP to update: %s", public_ip)
        for record in domain_records:
            if not isinstance(record, dict) or "name" not in record:
                continue
            domain_name = record["name"]
            domain_ip = record.get("content", "<no content>")
            LOGGER.info("Current IP for %s: %s", domain_name, domain_ip)

            if record is None:
                LOGGER.error("DNS record for %s not found.", domain_name)
                continue

            if public_ip != record["content"]:
                update_dns_record_content(record, public_ip)
            else:
                LOGGER.info(
                    "IP addresses are the same for %s. No update needed.", domain_name
                )

            if UPDATE_TYPE is True:
                check_and_update_dns_record_type(record, domain_name)
            if UPDATE_PROXY is True:
                check_and_update_dns_record_proxy(record, domain_name)
            if UPDATE_TTL is True:
                check_and_update_dns_record_ttl(record, domain_name)

    else:
        LOGGER.error("Failed to retrieve public IP. Skipping check and update.")


LOGGER.info("Schedule is set at %s minutes", SCHEDULE_MINUTES)
