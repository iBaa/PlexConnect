PlexConnect on any non atv ios devices (jailbroken)



You can install everything from your IOS device if desired using the following
  Webserver hosting your cert or a website e.g. www.zippyshare.com
  Safari download manager (Cydia)
  ifile (cydia)

Install cydelete & python using cydia from this repo (note you may need to install python a few times from the repo):
  http://cydia.myrepospace.com/plexconnect
  
Install wget on your IOS device
  "apt-get install wget"

Install plexconnect in /Applications/PlexConnect on the jailbroken ios device
  "chmod +x /Applications/PlexConnect/support/IOS_jailbreak/install.bash"
  prior to running issue this command
  "./install.bash"
  install by using this command

Respring or restart your IOS device

To keep plexconnect running without your wifi shutting off 
  turn on airplay mode
  reconnect desired wifi
  restart ios device
  unlock ios device to enable wifi while in airplane mode

To use an appletv and an ios device hosting plexconnect away from your pms server remotely use myplex which is the easiest method. 

An alternative method is by port forwarding your port_pms on your router and edit your pms allow without auth to include your local wan ip/subnet,local lan ip/subnet,remote wan ip/subnet e.g. 

11.22.33.44.55/255.255.255.0,192.168.1.101/255.255.255.0,55.44.33.22.11/255.255.255.0

Also you must edit your settings.cfg to point back to your pms server e.g.

[PlexConnect]
port_pms = 32400 (if this your pms port)
port_webserver = 80
ip_plexconnect = 0.0.0.0
certfile = ./assets/certificates/trailers.pem
ip_dnsmaster = 8.8.8.8
loglevel = Normal
enable_dnsserver = True
logpath = .
ip_pms = yourdyndns.com or wan ip (no http prefix)
enable_plexgdm = False
hosttointercept = trailers.apple.com
port_ssl = 443
enable_webserver_ssl = True
prevent_atv_update = True
port_dnsserver = 53
enable_plexconnect_autodetect = True




