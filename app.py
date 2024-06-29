from flask import Flask, render_template, request, redirect, url_for, jsonify
from network_scanner import scan_network, full_port_scan, get_manufacturer
from getmac import get_mac_address
from ip_manager import add_scan_result, get_scan_results, remove_scan_result, update_scan_result
from scheduler import save_schedule, get_schedules, add_scan_to_scheduler, is_ip_scheduled, remove_scheduled_scan
import docker_manager

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/pings')
def pings():
    saved_ips = get_scan_results()
    scheduled_scans = get_schedules()
    return render_template('pings.html', saved_ips=saved_ips, scheduled_scans=scheduled_scans)

@app.route('/rescan', methods=['POST'])
def rescan():
    network = "192.168.1.0/24"
    reachable_devices = scan_network(network)
    return jsonify(reachable_devices)

@app.route('/scan_ports', methods=['POST'])
def scan_ports():
    data = request.json
    ip_address = data.get('ip_address')
    if ip_address:
        try:
            open_ports = full_port_scan(ip_address)
            mac = get_mac_address(ip=ip_address)
            manufacturer = get_manufacturer(mac)
            add_scan_result(ip_address, mac=mac, manufacturer=manufacturer, open_ports=open_ports)
            return jsonify({'ip_address': ip_address, 'open_ports': open_ports})
        except Exception as e:
            update_scan_result(ip_address, failed=True)
            return jsonify({'error': str(e)}), 500
    return jsonify({'error': 'No IP address provided'}), 400

@app.route('/remove_ip', methods=['POST'])
def remove_ip():
    ip_address = request.form['ip_address']
    remove_scan_result(ip_address)
    remove_scheduled_scan(ip_address)
    return redirect(url_for('pings'))

@app.route('/schedule_scan', methods=['POST'])
def schedule_scan():
    data = request.json
    ip_address = data.get('ip_address')
    interval = data.get('interval')
    interval_type = data.get('interval_type')
    created_at = data.get('created_at')
    if is_ip_scheduled(ip_address):
        return jsonify({'success': False, 'message': 'This IP address already has a scheduled scan.'}), 400
    if ip_address and interval and interval_type and created_at:
        schedule = {
            'ip_address': ip_address,
            'interval': interval,
            'interval_type': interval_type,
            'created_at': created_at
        }
        save_schedule(schedule)
        add_scan_to_scheduler(schedule)
        update_scan_result(ip_address, scheduled=True)
        return jsonify({'success': True})
    return jsonify({'success': False}), 400

@app.route('/remove_scheduled_scan', methods=['POST'])
def remove_scheduled_scan_route():
    data = request.json
    ip_address = data.get('ip_address')
    if ip_address:
        try:
            remove_scheduled_scan(ip_address)
            update_scan_result(ip_address, scheduled=False)
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    return jsonify({'success': False, 'error': 'No IP address provided'}), 400

@app.route('/docker')
def docker():
    return render_template('docker.html')

@app.route('/docker/containers')
def list_docker_containers():
    containers = docker_manager.list_containers()
    return jsonify(containers=containers)

@app.route('/docker/containers/<container_id>/stop', methods=['POST'])
def stop_docker_container(container_id):
    message = docker_manager.stop_container(container_id)
    return jsonify(message=message)

@app.route('/docker/containers/<container_id>/start', methods=['POST'])
def start_docker_container(container_id):
    message = docker_manager.start_container(container_id)
    return jsonify(message=message)

@app.route('/docker/containers/<container_id>/logs', methods=['GET'])
def get_docker_container_logs(container_id):
    logs = docker_manager.get_container_logs(container_id)
    return jsonify(logs=logs)

@app.route('/proxmox')
def proxmox():
    return render_template('proxmox.html')

if __name__ == '__main__':
    app.run(debug=True)
