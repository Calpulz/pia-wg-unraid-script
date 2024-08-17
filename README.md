# pia-wg
A WireGuard configuration utility for Private Internet Access

This is a Python utility that generates WireGuard configuration files for the Private Internet Access VPN service. This allows you to take advantage of the WireGuard protocol without relying on PIA's proprietary client.

This was created by reverse engineering the [manual-connections](https://github.com/pia-foss/manual-connections) script released by PIA. At this stage, the tool is a quick and dirty attempt to get things working. It could break at any moment if PIA makes changes to their API.

## UNRAID USERSCRIPT

This has been modified to work with UNRAID OS though the UserScripts Plugin. Wireguard Config file (wg.conf) and UNRAID config file (wg.cfg) are both generated and placed inside the wireguard directory.

**This was mainly done for my own use. It may break or not function with different setups.**

## REQUIREMENTS

- **THIS WILL ONLY WORK IN UNRAID OS**
- UserScripts plugin by	Andrew Zawadzki **MUST** be installed
- NerdTools plugin by UnRAIDES **MUST** be installed with the following enabled:
     - python-pip
     - python-setuptools
     - python3

## INSTRUCTIONS
- In the UNRAID WebGUI, go to Settings>UserScripts>ADD NEW SCRIPT
- Name the Script. Example: "PIA Config Generator"
- Click the small cog by this new script and click "EDIT SCRIPT"
- Copy and paste the script below
```
#!/bin/bash
git clone https://github.com/Calpulz/pia-wg-unraid-script.git
cd pia-wg-unraid-script


python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

python generate-config.py --region "REGION" --username "USERNAME" --password "PASSWORD" --config "CONFIGNAME" --config-dir "/etc/wireguard"

cd ..
rm -rf "pia-wg-unraid-script"
```
- The above script will pull this repo, setup and start the Python Virtual Enviroment, run the Configuration Generation Script and then clean up the Virtual Enviroment.
- After the script has run, 2 config files will have been generated in the output directory. For Example, wg1.conf and wg1.cfg.
- **NEXT IS IMPORTANT**
- In the UNRAID WebGUI go to Settings>VPN Manager
- You should now see the new tunnel. Before you activate the tunnel you must add names to "Local Name" and "Peer Name" and then click "APPLY".
- **UNRAID OS will then add extra configuration to the config files that were generated that is needed for the tunnel to function!**
- Now you can enable the tunnel.
- Simply change any dockers to use this new network for them to use the PIA VPN.
- It is suggested that you add your prefered DNS into the Extra Parameters for each docker using this tunnel to avoid DNS leaks. For example: --dns=8.8.8.8

## Configuration
All configuration is done inside the UNRAID UserScript by editing the following line:
```
python generate-config.py --region "REGION" --username "USERNAME" --password "PASSWORD" --config "CONFIGNAME" --config-dir "/etc/wireguard"
```


```
Arguments:
  --region "REGION"          **Allowed values are** AU Adelaide, AU Brisbane, AU
                             Melbourne, AU Perth, AU Sydney, Albania, Algeria,
                             Andorra, Argentina, Armenia, Australia Streaming
                             Optimized, Austria, Bahamas, Bangladesh, Belgium,
                             Bolivia, Bosnia and Herzegovina, Brazil, Bulgaria, CA
                             Montreal, CA Ontario, CA Ontario Streaming Optimized,
                             CA Toronto, CA Vancouver, Cambodia, Chile, China,
                             Colombia, Costa Rica, Croatia, Cyprus, Czech Republic,
                             DE Berlin, DE Frankfurt, DE Germany Streaming
                             Optimized, DK Copenhagen, DK Streaming Optimized, ES
                             Madrid, ES Valencia, Ecuador, Egypt, Estonia, FI
                             Helsinki, FI Streaming Optimized, France, Georgia,
                             Greece, Greenland, Guatemala, Hong Kong, Hungary, IT
                             Milano, IT Streaming Optimized, Iceland, India,
                             Indonesia, Ireland, Isle of Man, Israel, JP Streaming
                             Optimized, JP Tokyo, Kazakhstan, Latvia,
                             Liechtenstein, Lithuania, Luxembourg, Macao, Malaysia,
                             Malta, Mexico, Moldova, Monaco, Mongolia, Montenegro,
                             Morocco, NL Netherlands Streaming Optimized, Nepal,
                             Netherlands, New Zealand, Nigeria, North Macedonia,
                             Norway, Panama, Peru, Philippines, Poland, Portugal,
                             Qatar, Romania, SE Stockholm, SE Streaming Optimized,
                             Saudi Arabia, Serbia, Singapore, Slovakia, Slovenia,
                             South Africa, South Korea, Sri Lanka, Switzerland,
                             Taiwan, Turkey, UK London, UK Manchester, UK
                             Southampton, UK Streaming Optimized, US Alabama, US
                             Alaska, US Arkansas, US Atlanta, US Baltimore, US
                             California, US Chicago, US Connecticut, US Denver, US
                             East, US East Streaming Optimized, US Florida, US
                             Honolulu, US Houston, US Idaho, US Indiana, US Iowa,
                             US Kansas, US Kentucky, US Las Vegas, US Louisiana, US
                             Maine, US Massachusetts, US Michigan, US Minnesota, US
                             Mississippi, US Missouri, US Montana, US Nebraska, US
                             New Hampshire, US New Mexico, US New York, US North
                             Carolina, US North Dakota, US Ohio, US Oklahoma, US
                             Oregon, US Pennsylvania, US Rhode Island, US Salt Lake
                             City, US Seattle, US Silicon Valley, US South
                             Carolina, US South Dakota, US Tennessee, US Texas, US
                             Vermont, US Virginia, US Washington DC, US West, US
                             West Streaming Optimized, US West Virginia, US
                             Wilmington, US Wisconsin, US Wyoming, Ukraine, United
                             Arab Emirates, Uruguay, Venezuela, Vietnam

  --username "USERNAME"      PIA account username

  --password "PASSWORD"      PIA account password

  --config "CONFIGNAME"      Name of the generated config files. Make sure no other config exists with this name. E.G wg0, wg1, wg2

  --config-dir "DIRECTORY"   Directory where config files will be generated. Default is /etc/wireguard
```
## Example
```
python generate-config.py --region "Norway" --username "a123456" --password "astrongpassword" --config "wg0" --config-dir "/etc/wireguard"
```
