from scapy.all import ARP, Ether, srp
import socket
import concurrent.futures
from mac_manager import get_manufacturer

def scan_network(network):
    # Prepare the ARP request packet
    arp = ARP(pdst=network)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp
    result = srp(packet, timeout=3, verbose=0)[0]

    devices = []
    # Iterate over the result and append the devices to the list
    for sent, received in result:
        mac = received.hwsrc
        manufacturer = get_manufacturer(mac)
        devices.append({'ip': received.psrc, 'mac': mac, 'manufacturer': manufacturer})

    # Sort the devices by the last octet of the IP address
    devices.sort(key=lambda x: int(x['ip'].split('.')[-1]))

    # Print the devices
    for device in devices:
        print(f"IP: {device['ip']}\tMAC: {device['mac']}\tManufacturer: {device['manufacturer']}")

    return devices

def scan_port(ip, port):
    if port % 500 == 0:
        print(f"Scanning port {port}/65535", end="\r", flush=True)
    # Create a socket object
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    # Check if the port is open
    result = sock.connect_ex((ip, port))
    sock.close()
    # Return the port if it's open
    return port if result == 0 else None

def full_port_scan(ip):
    open_ports = []
    # Use ThreadPoolExecutor to scan all ports
    with concurrent.futures.ThreadPoolExecutor(max_workers=1000) as executor:
        # Submit all ports to be scanned
        futures = [executor.submit(scan_port, ip, port) for port in range(1, 65536)]
        # Iterate over the completed futures
        for future in concurrent.futures.as_completed(futures):
            port = future.result()
            # If the port is open, add it to the list
            if port:
                open_ports.append(port)
    # Sort the open ports
    open_ports.sort()
    print(f"Open ports for {ip}: {open_ports}")
    return open_ports
