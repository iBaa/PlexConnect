# OpenConnect

How to install  (if updating OpenConnect you must perform steps 1 & 2 again to get the updated scripts prior to launching the new app that you can download in step 3)

Step 1. Kill plexconnect if its running or unload your plist if used to autostart PlexConnect.

Step 2. Clone the repo then download the entire code here (download zip) http://alturl.com/4ib3f then enter these commands into terminal (put this in a non system folder like documents or something to avoid database errors that may prevent OpenConnect or webconnect from functioning)

Proper PlexConnect installation:
```sh
sudo su
cd /Applications
git clone https://github.com/iBaa/PlexConnect.git
```
Copy the update/OSX folder to the cloned repo base PlexConnect directory then using terminal naviagate to the new /update/OSX folder <-----OSX is a subfolder of Update:
```sh
chmod +x install.bash
./install.bash
```
Or enter these commands into terminal if you have an existing cloned PlexConnect folder:
```sh
sudo su 
## Navigate to your PlexConnect base directory
mkdir -p /update/OSX
## Copy the contents from the zip's folder /update/OSX to the new update/OSX folder from here 
## (download zip): http://alturl.com/4ib3f
Navigate to the new /update/OSX folder <-----OSX is a subfolder of Update.
chmod +x install.bash
./install.bash
```
Step 3. To install OpenConnect app on osx simply run this app (OpenConnect has built-in in PlexConnect updater function):

https://www.dropbox.com/sh/t45w85ktydh0dvu/6-8W2POoM4

A few notes about OpenConnect:

OpenConnect requires a plist for the update function to work just use the expert or guide mode to install the PlexConnect autostarting plist. Finally see if your appletv is displaying PlexConnect, if it is your plist has been properly installed. This app is designed to allow you to keep PlexConnect up to date if there is anything you want to backup please do so prior to using this app.

# WebConnect

How to install (Install OpenConnect prior to WebConnect using the above instructions)

Step 1. Apache2 server on a unused port (plexconnect runs on 53, 80, 443) edit /etc/apache2/httpd.conf hosts section to change the listen port:

http://clickontyler.com/blog/2012/02/web-sharing-mountain-lion/

Step 2. Edit your sudoers file and add this section:
```sh
_www    ALL= NOPASSWD: /usr/bin/createcert.bash,/usr/bin/createplist.bash,/usr/bin/update.bash,/usr/bin/start.bash,/usr/bin/stop.bash,/usr/bin/restart.bash
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

How to uninstall OpenConnect, WebConnect and PlexConnect's autoloading plist. Enter these commands in terminal:
```sh
sudo su
# Navigate to the /update/OSX folder
./uninstall.bash
```
You can remove the /update/OSX folder manually using finder and the OpenConnect app wherever you may have placed it. You will need to edit your sudoers file as well to complete the removal pocess.
