PlexConnect on any non atv iOS devices (jailbroken)

You can install everything from your iOS device if desired using the following
  webserver or a website hosting your cert
  safari download manager (Cydia)
  ifile (cydia)
  mobileterminal (cydia app)

To keep plexconnect running without your wifi shutting off 
  turn on airplay mode (this will disable your wifi)
  reconnect desired wifi
  restart iOS device
  unlock iOS device to enable wifi while in airplane mode

grab these .deb files here only choose ios 6.x or ios 7.x:

https://www.dropbox.com/sh/cghw1w6khwqq8rg/8ejDwZ7Rpe

ssh into your ios device and enter the following commands and install all these packages wget, python):

apt-get install git
apt-get install wget <-----you may already have this
apt-get update
apt-get upgrade
dpkg -i python_2.7.3-3_iphoneos-arm.deb       <------copy over python_2.7.3-3_iphoneos-arm.deb to ios device via sftp prior to running this command (use filezilla or another sftp program)
dpkg -i apt-get -f install
dpkg -i plexconnect.deb      <------copy over plexconnect.deb to ios device via sftp prior to running this command (use filezilla or another sftp program)

Note: You may need to change or copy your trailers.pem and edit your settings.cfg using iFile to match your desired configuration if need be. Installing plexconnect from the repo will generate certificates for you so you need to delete those if you are going to use your own. So your choices are to copy the new generated trailers.pem from your ios device to your atv or copy your old trailers.pem from another device to your atv examples: Mac, pc, linux, nas, rpi that was hosting plexconnect prior. You need matching certs on both device for it to work properly. I prefer to just use one universal cert set for all of my plexconnect hosts and apple tv's.

Set AppleTV DNS to manual pointed at iOS device IP address
  done!
  
If Mobile Substrate is fixed in the future you can run this command  
  “./default.bash"
  this will restore PlexConnect.bash to defaults for universal network readiness

To use an appletv and an ios device hosting plexconnect away from your pms server remotely use myplex which is the easiest & most secure method.
