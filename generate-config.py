#!/usr/bin/env python

from piawg import piawg
from datetime import datetime
from wgconfig import WGConfig
import argparse, os, sys, subprocess

# comment to debug
sys.tracebacklimit = 0

def generate_public_key(private_key):
    """Generate a WireGuard public key from a private key."""
    process = subprocess.Popen(['wg', 'pubkey'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate(input=private_key.encode())
    if process.returncode != 0:
        raise Exception(f"Failed to generate public key: {stderr.decode().strip()}")
    return stdout.decode().strip()

def main():
    pia = piawg()
    regions = sorted([x for x in pia.server_list if 'wg' in pia.server_list[x]['servers']])

    # Parse arguments
    parser = argparse.ArgumentParser(description='Generate PIA wireguard config')
    parser.add_argument('-r', '--region', dest='region', choices=regions, required=True, help='Select a region', metavar='')
    parser.add_argument('-f', '--config', help='Name of the generated config file (without extension)', required=True)
    parser.add_argument('--username', required=True, help='PIA username')
    parser.add_argument('--password', required=True, help='PIA password')
    parser.add_argument('--config-dir', default='.', help='Directory to save the generated config file (default: current directory)')
    args = parser.parse_args()

    # Select region
    region = args.region
    print("Selected region: '{}'".format(region))
    pia.set_region(region)

    # Generate public and private key pair
    pia.generate_keys()

    # Get credentials from arguments
    username = args.username
    password = args.password

    # Get token
    if not pia.get_token(username, password):
        print("Error logging in with provided credentials.")
        sys.exit(1)
    print("Login successful!")

    # Add key
    status, response = pia.addkey()
    if status:
        print("Added key to server!")
    else:
        print("Error adding key to server")
        print(response)
        sys.exit(1)

    # Build config
    config_name = args.config
    config_file = f"{config_name}.conf"

    # Ensure the config directory exists
    config_dir = os.path.abspath(args.config_dir)
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)

    # Combine the config directory and config file name
    config_path = os.path.join(config_dir, config_file)
    print("Saving configuration file to {}".format(config_path))

    wgc = WGConfig(config_path)
    wgc.add_attr(None, 'Address', pia.connection['peer_ip'])
    wgc.add_attr(None, 'PrivateKey', pia.privatekey)
    for dns_server in pia.connection['dns_servers'][0:2]:
        wgc.add_attr(None, 'DNS', dns_server)
    peer = pia.connection['server_key']
    wgc.add_peer(peer, '# ' + pia.region)
    wgc.add_attr(peer, 'Endpoint', pia.connection['server_ip'] + ':1337')
    wgc.add_attr(peer, 'AllowedIPs', '0.0.0.0/0')
    wgc.add_attr(peer, 'PersistentKeepalive', '25')

    # Add the comments under [Interface] and [Peer]
    with open(config_path, 'w') as config_file:
        config_file.write("[Interface]\n")
        config_file.write("#\n")
        config_file.write(f"PrivateKey = {pia.privatekey}\n")
        config_file.write(f"Address = {pia.connection['peer_ip']}\n")
        config_file.write(f"DNS = {', '.join(pia.connection['dns_servers'][0:2])}\n\n")
        config_file.write("[Peer]\n")
        config_file.write("#\n")
        config_file.write(f"PublicKey = {pia.connection['server_key']}\n")
        config_file.write(f"Endpoint = {pia.connection['server_ip']}:1337\n")
        config_file.write("AllowedIPs = 0.0.0.0/0\n")
        config_file.write("PersistentKeepalive = 25\n")

    print(f"Configuration saved to {config_path}")

    # Generate the public key for the .cfg file from the private key
    public_key_cfg = generate_public_key(pia.privatekey)

    # Generate the .cfg file with the same name as the config
    cfg_file_path = os.path.join(config_dir, f"{config_name}.cfg")
    network = pia.connection['peer_ip'].rsplit('.', 1)[0] + ".0/24"  # Adjust the network to match "10.26.147.0/24"

    cfg_content = f"""
PublicKey:0="{public_key_cfg}"
PROT:0=""
Network:0="{network}"
Endpoint:0=""
UPNP:0="no"
DROP:0=""
RULE:0=""
TYPE:1="8"
Address:1=""
"""

    # Save the .cfg file
    with open(cfg_file_path, 'w') as cfg_file:
        cfg_file.write(cfg_content.strip())

    print(f"Configuration saved to {cfg_file_path}")

if __name__ == '__main__':
    main()
