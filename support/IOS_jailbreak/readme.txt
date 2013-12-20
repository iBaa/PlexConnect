PlexConnect on any non atv ios devices (jailbroken)



Install Python on any non atv ios devices
(current version: python_2.7.3-3_iphoneos-arm.deb)
- download "https://yangapp.googlecode.com/files/python_2.7.3-3_iphoneos-arm.deb"
- SFTP "python_2.7.3-3_iphoneos-arm.deb" to your aTV
- SSH into aTV and execute...
  "apt-get update"
  "apt-get upgrade"
  just to make sure you have the latest packages
  "apt-get install cydia"
  "apt-get install python"
  this will pull and install python 2.5.1 with all dependencies
  "dpkg -i python_2.7.3-3_iphoneos-arm.deb"
  this will update python to 2.7.3
  "apt-get -f install"
  this will fix any errors if encountered

Install plexconnect in /Applications/PlexConnect on the jailbroken ios device
  "chmod +x /Applications/PlexConnect/support/IOS_jailbreak/install.bash"
  prior to running issue this command
  "./install.bash"
  install by using this command

To keep plexconnect running without your wifi shutting off 
  turn on airplay mode
  reconnect desired wifi
  restart ios device
  unlock ios device to enable wifi while in airplane mode


