PlexConnect on aTV (jailbroken)



Install Python on aTV
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

Push PlexConnect to aTV
- SFTP into aTV and copy the complete PlexConnect directory to eg. /Application/PlexConnect.


OPTION A - run PlexConnect as always, re-using trailers.apple.com

- make sure you have good certs in /PlexConnect/assets/certificates
  if not, generate and add them...

- SFTP PlexConnect/support/aTV_jailbreak/Settings_Trailers.cfg to PlexConnect/Settings.cfg
  overwrite the later if already there
  this brings new defaults for PlexConnect@aTV, like disabling DNSServer

/etc/hosts
- add content of PlexConnect/support/aTV_jailbreak/hosts_addon_PlexConnect to /etc/hosts
  this redirects the trailer app back to aTV itself, replacing the DNSServer


OPTION B - create own PlexConnect button

- SFTP PlexConnect/support/aTV_jailbreak/Settings_PlexConnect.cfg to PlexConnect/Settings.cfg
  overwrite the later if already there
  this brings new defaults for PlexConnect@aTV, like disabling DNSServer/WebServer SSL

Install PlexConnect button to aTV home screen
- SSH into aTV
- CD into the PlexConnect directory. Eg. "cd /Application/PlexConnect"
- run "./support/aTV_jailbreak/install_button.bash"
  this will set up 
     /Library/Managed Preferences/mobile/com.apple.frontrow.plist
     /User/Library/Application Support/Front Row/ExtraInternetCategories.plist
     ./support/aTV_jailbreak/bag.plist
  and thereby enabling the AddSite hack tailored to PlexConnect.

Thanks to D. Schuetz! (https://intrepidusgroup.com/insight/2013/09/rpi-atv/)


FINISH INSTALLATION

Install PlexConnect as daemon
- SSH into aTV
- CD into the PlexConnect directory. Eg. "cd /Application/PlexConnect"
- run "./support/aTV_jailbreak/install.bash"

/etc/hosts
- optional: add PlexConnect/support/aTV_jailbreak/hosts_addon_preventATVUpdate
  this prevents aTV update

Reboot

Done!



Debug PlexConnect

check processes
- "ps -ef" should find 3 Python/PlexConnect related processes

check launchctl
- "launchctl list | grep .plexconnect." should give "<PID>  -  com.plex.plexconnect.bash.plist"

check StdOut, StdErr
- in com.plex.plexconnect.bash.plist swap comments for StandardOutPath, StandardErrorPath payload
  dump data to real file: ./PlexConnect_stdout.log, ./PlexConnect_stderr.log
  prevent output (dflt): /dev/null
- run "./support/aTV_jailbreak/uninstall.bash"
- run "./support/aTV_jailbreak/install.bash"
