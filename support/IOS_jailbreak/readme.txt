PlexConnect on any non atv ios devices (jailbroken)



You can install everything from your IOS device if desired using the following
  webserver or a website hosting your cert
  safari download manager (Cydia)
  ifile (cydia)

To keep plexconnect running without your wifi shutting off 
  turn on airplay mode (this will disable your wifi)
  reconnect desired wifi
  restart ios device
  unlock ios device to enable wifi while in airplane mode

Using cydia add and install all packages from this repo: 
  http://cydia.myrepospace.com/plexconnect

Install plexconnect in /Applications/PlexConnect on the jailbroken ios device
  "chmod +x /Applications/PlexConnect/support/IOS_jailbreak/install.bash"
  prior to running issue this command
  "./install.bash"
  install by using this command
  
Set AppleTV DNS to manual pointed at iOS device IP address
  done!
  
If Mobile Substrate is fixed in the future you can run this command  
  "./unfix.bash"
  this will restore PlexConnect.bash to defaults for universal network readiness

To use an appletv and an ios device hosting plexconnect away from your pms server remotely use myplex which is the easiest method. 

An alternative method is by port forwarding your port_pms on your router and editing your pms allow without auth to include your local wan ip/subnet,local lan ip/subnet,remote wan ip/subnet e.g. 

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
