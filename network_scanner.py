from scapy.all import ARP, Ether, srp
import socket
import concurrent.futures
from mac_manager import get_manufacturer

def scan_network(network):
    arp = ARP(pdst=network)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp
    result = srp(packet, timeout=3, verbose=0)[0]

    devices = []
    for sent, received in result:
        mac = received.hwsrc
        manufacturer = get_manufacturer(mac)
        devices.append({'ip': received.psrc, 'mac': mac, 'manufacturer': manufacturer})

    devices.sort(key=lambda x: int(x['ip'].split('.')[-1]))

    for device in devices:
        print(f"IP: {device['ip']}\tMAC: {device['mac']}\tManufacturer: {device['manufacturer']}")

    return devices

def scan_port(ip, port):
    if port % 500 == 0:
        print(f"Scanning port {port}/65535", end="\r", flush=True)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex((ip, port))
    sock.close()
    return port if result == 0 else None

def full_port_scan(ip):
    open_ports = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=1000) as executor:
        futures = [executor.submit(scan_port, ip, port) for port in range(1, 65536)]
        for future in concurrent.futures.as_completed(futures):
            port = future.result()
            if port:
                open_ports.append(port)
    open_ports.sort()
    print(f"Open ports for {ip}: {open_ports}")
    return open_ports
