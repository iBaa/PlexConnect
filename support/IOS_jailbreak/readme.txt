PlexConnect on any non atv iOS devices (jailbroken)



You can install everything from your iOS device if desired using the following
  webserver or a website hosting your cert
  safari download manager (Cydia)
  ifile (cydia)

To keep plexconnect running without your wifi shutting off 
  turn on airplay mode (this will disable your wifi)
  reconnect desired wifi
  restart iOS device
  unlock iOS device to enable wifi while in airplane mode

Using cydia add and install all these packages from this repo (wget, apt strict 0.7, python):
  http://cydia.myrepospace.com/plexconnect
Even if they fail installation ignore it and continue they are installed.

Once all of these are installed using the same repo install plexconnect
When it is complete it will reboot your device

Note: You may need to change or copy your trailers.pem and edit your settings.cfg using iFile to match your desired configuration if need be. Installing plexconnect from the repo will generate certificates for you so you need to delete those if you are going to use your own. So your choices are to copy the new generated trailers.pem from your ios device to your atv or copy your old trailers.pem from another device to your atv examples: Mac, pc, linux, nas, rpi that was hosting plexconnect prior. You need matching trailers.pem's on both device for it to work properly. I prefer to just use one universal trailers.pem for all of my plexconnect hosts and apple tv's.

  
Set AppleTV DNS to manual pointed at iOS device IP address
  done!
  
If Mobile Substrate is fixed in the future you can run this command  
  “./default.bash"
  this will restore PlexConnect.bash to defaults for universal network readiness

To use an appletv and an ios device hosting plexconnect away from your pms server remotely use myplex which is the easiest & most secure method. 

An alternative method which I prefer is by port forwarding your port_pms on your router e.g 324000 to your pms host and editing your pms allow without auth to include your local wan ip/subnet,local lan ip/subnet,remote wan ip/subnet e.g. 

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
