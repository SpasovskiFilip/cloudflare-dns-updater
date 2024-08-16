"""
DNS Updater
Original Author: Alexandru-Ioan Plesoiu
Contributor: Filip Spasovski
Original GitHub: https://github.com/SpasovskiFilip
Contributor GitHub: 
Documentation: https://github.com/SpasovskiFilip/dns-updater

DNS Updater is a Python-based tool that automatically updates Cloudflare DNS records
with your public IP address. If your server's IP address changes frequently or you
have a dynamic IP, this tool ensures that your domains and subdomains always point
to the correct server. It can handle multiple domains and subdomains from multiple
zones, with proxying enabled or disabled. The tool runs checks and updates every
5 minutes and includes redundancy for IP checking services.
"""

import time
import schedule
from functions import check_and_update_dns, SCHEDULE_MINUTES

# Schedule the check and update process to run every X minutes
schedule.every(SCHEDULE_MINUTES).minutes.do(check_and_update_dns).run()

# Main loop
while True:
    schedule.run_pending()
    time.sleep(1)
