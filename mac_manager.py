import json
import os

OUI_FILE = 'oui.txt'
MAC_MANUFACTURERS_FILE = 'data/mac_manufacturers.json'

def load_oui_list():
    oui_dict = {}
    # Check if the OUI file exists
    if not os.path.exists(OUI_FILE):
        print(f"OUI file '{OUI_FILE}' not found.")
        return oui_dict

    # Open the OUI file and read the lines
    with open(OUI_FILE, 'r') as file:
        for line in file:
            if '(base 16)' in line:
                parts = line.split('(base 16)')
                if len(parts) == 2:
                    # Extract the OUI and manufacturer taking into account the format of the file
                    oui = parts[0].strip().replace('-', ':')
                    manufacturer = parts[1].strip()
                    oui_dict[oui] = manufacturer
    return oui_dict

def load_mac_manufacturers():
    # Check if the MAC manufacturers file exists
    if os.path.exists(MAC_MANUFACTURERS_FILE):
        with open(MAC_MANUFACTURERS_FILE, 'r') as file:
            # Load the MAC manufacturers from the file
            return json.load(file)
    return {}

def save_mac_manufacturers(mac_manufacturers):
    # Save the MAC manufacturers to the file
    with open(MAC_MANUFACTURERS_FILE, 'w') as file:
        json.dump(mac_manufacturers, file, indent=4)

def get_manufacturer_from_file(mac):
    # Load the MAC manufacturers from the file
    mac_manufacturers = load_mac_manufacturers()
    return mac_manufacturers.get(mac)

def add_manufacturer_to_file(mac, manufacturer):
    # Load the MAC manufacturers from the file
    mac_manufacturers = load_mac_manufacturers()
    mac_manufacturers[mac] = manufacturer
    # Save the MAC manufacturers to the file
    save_mac_manufacturers(mac_manufacturers)

def get_manufacturer(mac):
    # Check if the manufacturer is cached
    cached_manufacturer = get_manufacturer_from_file(mac)
    if cached_manufacturer:
        print(f"Retrieved manufacturer {cached_manufacturer} from file for MAC address {mac}")
        # Return the cached manufacturer
        return cached_manufacturer

    # Load the OUI list and prepare the OUI from the MAC address
    oui_dict = load_oui_list()
    oui = mac.upper()[:8]
    oui = oui.replace(':', '')
    oui = oui.upper()
    # Get the manufacturer from the OUI list
    manufacturer = oui_dict.get(oui, "Unknown")

    # Add the manufacturer to the file
    if manufacturer != "Unknown":
        print(f"Found manufacturer {manufacturer} for MAC address {mac} in the OUI list")
        add_manufacturer_to_file(mac, manufacturer)
    else:
        print(f"Failed to get manufacturer for MAC address {mac}")

    # Return the manufacturer
    return manufacturer
