#!/usr/bin/env python

from piawg import piawg
from datetime import datetime
from wgconfig import WGConfig
import argparse, os, sys

# comment to debug
sys.tracebacklimit = 0

def main():
    pia = piawg()
    regions = sorted([x for x in pia.server_list if 'wg' in pia.server_list[x]['servers']])

    # Parse arguments
    parser = argparse.ArgumentParser(description='Generate PIA wireguard config')
    parser.add_argument('-r', '--region', dest='region', choices=regions, required=True, help='Select a region', metavar='')
    parser.add_argument('-f', '--config', help='Name of the generated config file')
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
    if args.config:
        config_file = args.config
    else:
        timestamp = int(datetime.now().timestamp())
        location = pia.region.replace(' ', '-')
        config_file = 'PIA-{}-{}.conf'.format(location, timestamp)

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
    wgc.write_file()

if __name__ == '__main__':
    main()
