How to install OpenConnect (if updating OpenConnect you must perform steps 1 & 2 again to get the updated scripts prior to launching the new app that you can download in step 3)

Step 1

-- kill plexconnect if its running or unload your plist if used to autostart PlexConnect
In your PlexConnect directory make these new folders /update/OSX <-----case sensitive (OSX is a subfolder of update)
Copy all the files from here to the new OSX folder you just created
(If you have a plist that autostarts PlexConnect you can ignore killing PlexConnect, OpenConnect will do this for you)

Step 2 enter these commands into terminal:

sudo su 
## Naviagate to your PlexConnect base directory
mkdir -p /update/OSX
## Naviagate to the new /update/OSX folder <-----OSX is a subfolder of Update.
./install.bash

step 3

-- To install OpenConnect app on osx simply run this app (OpenConnect has built-in in PlexConnect updater function):

-- https://www.dropbox.com/sh/t45w85ktydh0dvu/6-8W2POoM4

A few notes about OpenConnect:

OpenConnect requires a plist for the update function to work just use the expert or guide mode to install the PlexConnect autostarting plist. Finally see if your appletv is displaying PlexConnect if it is your plist has been properly installed. This app is designed to automatically keep PlexConnect up to date for you so if there is anything you want to backup please do so prior to using this app.

How to install WebConnect (repeate steps 1 & 2 above for the latest release to update)

1. Apache2 server on a unused port (plexconnect runs on 53, 80, 443) edit /etc/apache2/httpd.conf hosts section to change port. http://clickontyler.com/blog/2012/02/web-sharing-mountain-lion/

2. Edit your sudoers file and add this section:

_www    ALL= NOPASSWD: /usr/bin/createcert.bash,/usr/bin/createplist.bash,/usr/bin/update.bash,/usr/bin/start.bash,/usr/bin/stop.bash,/usr/bin/restart.bash

3. Navigate to your new PlexConnect/update/OSX folder then issue these command:

sudo su
./webconnect

4. Enter a similar link into your browser:

http://YOUR_LOCAL_IP_ADDRESS:YOUR_APACHE2_PORT/cgin-bin/bash.cgi

5. *Optional* Open up your apache port pointed to your PlexConnect host to mangage PlexConnect anywhere on any device/web-browser.
