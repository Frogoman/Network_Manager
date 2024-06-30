import json
import os
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from network_scanner import full_port_scan, get_manufacturer
from ip_manager import add_scan_result, update_scan_result

SCHEDULE_FILE_PATH = 'data/scan_schedules.json'

scheduler = BackgroundScheduler()

def load_schedules():
    # Load the schedules from the file
    if os.path.exists(SCHEDULE_FILE_PATH):
        with open(SCHEDULE_FILE_PATH, 'r') as file:
            return json.load(file)
    # Return an empty list if the file doesn't exist
    return []

def save_schedule(schedule):
    # Save the schedule to the file
    schedules = load_schedules()
    schedules.append(schedule)
    # Add the scan to the scheduler
    with open(SCHEDULE_FILE_PATH, 'w') as file:
        json.dump(schedules, file, indent=4)

def get_schedules():
    # Return the schedules
    return load_schedules()

def perform_scheduled_scan(ip_address):
    try:
        # Perform a full port scan
        open_ports = full_port_scan(ip_address)
        # Add the scan result to the database
        update_scan_result(ip_address, open_ports=open_ports, failed=False, scheduled=True)
    except Exception:
        update_scan_result(ip_address, failed=True, scheduled=True)

def add_scan_to_scheduler(schedule):
    # Add the scan to the scheduler
    ip_address = schedule['ip_address']
    interval = int(schedule['interval'])
    interval_type = schedule['interval_type']
    
    # Add the scan to the scheduler with the specified interval
    if interval_type == 'minutes':
        scheduler.add_job(perform_scheduled_scan, 'interval', minutes=interval, args=[ip_address], id=ip_address)
    elif interval_type == 'hours':
        scheduler.add_job(perform_scheduled_scan, 'interval', hours=interval, args=[ip_address], id=ip_address)

def load_existing_schedules():
    # Load the existing schedules and add them to the scheduler
    schedules = get_schedules()
    for schedule in schedules:
        add_scan_to_scheduler(schedule)

def is_ip_scheduled(ip_address):
    # Check if the IP address is scheduled for scanning
    return scheduler.get_job(ip_address) is not None

def remove_scheduled_scan(ip_address):
    # Get the job by id (ip_address) and remove it
    job = scheduler.get_job(ip_address)
    if job:
        job.remove()
    # Remove the schedule from the file
    schedules = get_schedules()
    schedules = [schedule for schedule in schedules if schedule['ip_address'] != ip_address]
    with open(SCHEDULE_FILE_PATH, 'w') as file:
        json.dump(schedules, file, indent=4)
    update_scan_result(ip_address, scheduled=False)

# Add a new schedule
scheduler.start()
load_existing_schedules()
