# OpenConnect

How to install  (if updating OpenConnect you must perform steps 1 & 2 again to get the updated scripts prior to launching the new app that you can download in step 3)

Step 1. Kill plexconnect if its running or unload your plist if used to autostart PlexConnect.

Step 2. To install OpenConnect app on osx simply run this app in guide mode (OpenConnect has built-in in PlexConnect updater function):

https://www.dropbox.com/sh/t45w85ktydh0dvu/6-8W2POoM4

A few notes about OpenConnect:

OpenConnect requires a plist for the update function to work just use the expert or guide mode to install the PlexConnect autostarting plist. Finally see if your appletv is displaying PlexConnect, if it is your plist has been properly installed. This app is designed to allow you to keep PlexConnect up to date if there is anything you want to backup please do so prior to using this app. The app installs PlexConnect in /Applications/PlexConnect so if there is something there please back it up and delete that folder in order for OpenConnect to work.

# WebConnect 
# *New* - now install from the OpenConnect App

*Old method* How to install (Install OpenConnect prior to WebConnect using the above instructions)

Step 1. Apache2 server on a unused port (plexconnect runs on 53, 80, 443) edit /etc/apache2/httpd.conf hosts section to change the listen port:

http://clickontyler.com/blog/2012/02/web-sharing-mountain-lion/

Step 2. Edit your sudoers file and add this section:
```sh
_www    ALL= NOPASSWD: /usr/bin/createcert.bash,/usr/bin/createplist.bash,/usr/bin/update.bash,/usr/bin/start.bash,/usr/bin/stop.bash,/usr/bin/restart.bash,/usr/bin/status.bash,/usr/bin/reboot.bash,/usr/bin/removecerts.bash,/usr/bin/createimovie.bash,/usr/bin/createwsj.bash,/usr/bin/lock.bash,/usr/bin/trash.bash
```
Step 3. Navigate to your new PlexConnect/update/OSX folder then issue these commands:
```sh
sudo su
./webconnect.bash
```
Step 4. Enter a similar link into your browser:
```sh
http://YOUR_LOCAL_IP_ADDRESS:YOUR_APACHE2_PORT/cgi-bin/bash.cgi
```
Step 5. *Optional* Open up your apache port pointed to your PlexConnect host to mangage PlexConnect anywhere on any device/web-browser.

# Uninstall

*Warning backup any files needed located in /Applications/PlexConnect prior to use this will remove your PlexConnect folder as well in /Applications*

How to uninstall OpenConnect, WebConnect and PlexConnect's autoloading plist. Enter these commands in terminal:
```sh
sudo su
cd /Applications/PlexConnect/update/OSX
./uninstall.bash
```
You will need to edit your sudoers file as well using visudo via terminal to complete the removal pocess if desired but it is not required and will not harm your system if your sudores file is left edited.
