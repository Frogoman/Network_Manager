import json
import os
from ipaddress import ip_address

SCAN_RESULTS_FILE_PATH = 'data/scan_results.json'

def load_scan_results():
    if os.path.exists(SCAN_RESULTS_FILE_PATH):
        with open(SCAN_RESULTS_FILE_PATH, 'r') as file:
            return json.load(file)
    return {}

def save_scan_results(results):
    sorted_results = dict(sorted(results.items(), key=lambda item: ip_address(item[0])))
    with open(SCAN_RESULTS_FILE_PATH, 'w') as file:
        json.dump(sorted_results, file, indent=4)

def add_scan_result(ip_address, mac=None, manufacturer=None, open_ports=None, failed=False, scheduled=False):
    results = load_scan_results()
    if ip_address not in results:
        results[ip_address] = {'mac': mac, 'manufacturer': manufacturer, 'ports': [], 'failed': failed, 'scheduled': scheduled}
    if mac is not None:
        results[ip_address]['mac'] = mac
    if manufacturer is not None:
        results[ip_address]['manufacturer'] = manufacturer
    if open_ports is not None:
        results[ip_address]['ports'] = open_ports
    if failed is not None:
        results[ip_address]['failed'] = failed
    if scheduled is not None:
        results[ip_address]['scheduled'] = scheduled
    save_scan_results(results)

def update_scan_result(ip_address, mac=None, manufacturer=None, open_ports=None, failed=None, scheduled=None):
    results = load_scan_results()
    if ip_address in results:
        if mac is not None:
            results[ip_address]['mac'] = mac
        if manufacturer is not None:
            results[ip_address]['manufacturer'] = manufacturer
        if open_ports is not None:
            results[ip_address]['ports'] = open_ports
        if failed is not None:
            results[ip_address]['failed'] = failed
        if scheduled is not None:
            results[ip_address]['scheduled'] = scheduled
        save_scan_results(results)

def get_scan_results():
    return load_scan_results()

def remove_scan_result(ip_address):
    results = load_scan_results()
    if ip_address in results:
        del results[ip_address]
        save_scan_results(results)
