"""
test_functions.py - Unit Tests for DNS Updater

This module contains pytest-based unit tests for the core functions of the DNS Updater project.
It verifies connectivity, DNS record retrieval, and public IP detection.

Test Functions:
    test_get_public_ip():
        Tests that a valid public IP address is returned.
    test_check_connectivity():
        Tests that the connectivity check passes.
    test_get_all_dns_records():
        Tests that DNS records can be retrieved.
    test_get_dns_records_by_comments():
        Tests that DNS records can be retrieved by comment keys.
    test_get_dns_records_by_domain_list():
        Tests that DNS records can be retrieved by domain and zone lists. (currently 0)
"""

from utils import get_public_ip
from functions import check_connectivity, get_all_dns_records
from functions import get_dns_records_by_comments, get_dns_records_by_domain_list
from functions import DOMAINS_LIST, CF_ZONE_ID_LIST, DNS_RECORD_COMMENT_KEY_LIST

def test_get_public_ip():
    """
    Test that get_public_ip() returns a valid IPv4 address string.
    """
    ip = get_public_ip()
    assert ip is not None and len(ip.split('.')) == 4

def test_check_connectivity():
    """
    Test that check_connectivity() returns True when configuration and network are valid.
    """
    assert check_connectivity() is True

def test_get_all_dns_records():
    """
    Test that get_all_dns_records() returns a non-empty list of DNS records.
    """
    assert len(get_all_dns_records()) != 0

def test_get_dns_records_by_comments():
    """
    Test that get_dns_records_by_comments() returns a non-empty list for valid comment keys.
    """
    assert len(get_dns_records_by_comments(CF_ZONE_ID_LIST, DNS_RECORD_COMMENT_KEY_LIST)) != 0

def test_get_dns_records_by_domain_list():
    """
    Test that get_dns_records_by_domain_list() returns an empty list for empty domains.
    """
    assert len(get_dns_records_by_domain_list(DOMAINS_LIST, CF_ZONE_ID_LIST)) == 0
