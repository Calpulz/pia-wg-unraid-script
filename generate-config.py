#!/usr/bin/env python

from piawg import piawg
from getpass import getpass
from datetime import datetime
from wgconfig import WGConfig
import argparse, os, sys, yaml

# comment to debug
sys.tracebacklimit = 0

def main():
    pia = piawg()
    regions = sorted([x for x in pia.server_list if 'wg' in pia.server_list[x]['servers']])

    # Parse arguments
    parser = argparse.ArgumentParser(description='Generate PIA wireguard config')
    parser.add_argument('-r', '--region', dest='region', choices=regions, help='Select a region', metavar='')
    parser.add_argument('-f', '--config', help='Name of the generated config file')
    parser.add_argument('--username', help='PIA username')
    parser.add_argument('--password', help='PIA password')
    args = parser.parse_args()

    # Load config from config.yaml if it exists
    config = None
    file = os.path.join(os.path.dirname(__file__), 'config.yaml')
    file = os.path.normpath(file)
    if os.path.exists(file):
        print("Loading config from {}".format(file))
        with open(file, 'r') as f:
            config = yaml.safe_load(f)

    # Select region from argument or config.yaml
    region = args.region or (config['pia']['region'] if config else None)
    if not region:
        print("Error: No region specified. Please provide a region with --region or in config.yaml.")
        sys.exit(1)

    print("Selected region: '{}'".format(region))
    pia.set_region(region)

    # Generate public and private key pair
    pia.generate_keys()

    # Get credentials from arguments or config.yaml
    username = args.username or (config['pia']['username'] if config else None)
    password = args.password or (config['pia']['password'] if config else None)

    if None in (username, password):
        print("Error: Username or password not provided. Please provide them via arguments or config.yaml.")
        sys.exit(1)

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
    print("Saving configuration file {}".format(config_file))
    if config_file[0] != '/':
        config_file = os.path.join(os.path.dirname(__file__), config_file)
        config_file = os.path.normpath(config_file)

    wgc = WGConfig(config_file)
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
