#!/bin/bash

## find update/OSX path
cd __DEFAULTPATH__
InstallerPath=${PWD}

## find PlexConnect main path
cd ../..
PlexConnectPath=${PWD}

## go back to InstallerPath
cd update/OSX

## install webconnect
plexweb.bash
plexwebwan.bash
plexwebios.bash
plexwebioswan.bash
plexweblist.bash
plexweblistwan.bash
cp bash.cgi /Library/WebServer/CGI-Executables/
cp ios.cgi /Library/WebServer/CGI-Executables/
cp list.cgi /Library/WebServer/CGI-Executables/
chmod +x /Library/WebServer/CGI-Executables/bash.cgi
chmod +x /Library/WebServer/CGI-Executables/ios.cgi
chmod +x /Library/WebServer/CGI-Executables/list.cgi

cp removecertsbash.bash /usr/bin
cp createcertbash.bash /usr/bin
cp createimoviebash.bash /usr/bin
cp createwsjbash.bash /usr/bin
cp createplistbash.bash /usr/bin
cp updatebash.bash /usr/bin
cp stopbash.bash /usr/bin
cp startbash.bash /usr/bin
cp restartbash.bash /usr/bin
cp statusbash.bash /usr/bin
cp rebootbash.bash /usr/bin
cp lockbash.bash /usr/bin
cp trashbash.bash /usr/bin
cp updatewcbash.bash /usr/bin
cp pmsscanbash.bash /usr/bin
cp shutdownbash.bash /usr/bin
cp sleepbash.bash /usr/bin
cp itunesbash.bash /usr/bin
cp quititunesbash.bash /usr/bin
cp wakebash.bash /usr/bin
cp logbash.bash /usr/bin
cp whobash.bash /usr/bin
cp tvbash.bash /usr/bin
cp sudoers /etc
cp httpd.conf /etc/apache2

chmod +x /usr/bin/removecertsbash.bash
chmod +x /usr/bin/createcertbash.bash
chmod +x /usr/bin/createimoviebash.bash
chmod +x /usr/bin/createwsjbash.bash
chmod +x /usr/bin/createplistbash.bash
chmod +x /usr/bin/updatebash.bash
chmod +x /usr/bin/stopbash.bash
chmod +x /usr/bin/startbash.bash
chmod +x /usr/bin/restartbash.bash
chmod +x /usr/bin/statusbash.bash
chmod +x /usr/bin/rebootbash.bash
chmod +x /usr/bin/lockbash.bash
chmod +x /usr/bin/trashbash.bash
chmod +x /usr/bin/updatewcbash.bash
chmod +x /usr/bin/pmsscanbash.bash
chmod +x /usr/bin/shutdownbash.bash
chmod +x /usr/bin/sleepbash.bash
chmod +x /usr/bin/itunesbash.bash
chmod +x /usr/bin/quititunesbash.bash
chmod +x /usr/bin/logbash.bash
chmod +x /usr/bin/whobash.bash
chmod +x /usr/bin/wakebash.bash
chmod +x /usr/bin/tvbash.bash

chmod 4755 /usr/bin/removecertsbash.bash
chmod 4755 /usr/bin/createcertbash.bash
chmod 4755 /usr/bin/createimoviebash.bash
chmod 4755 /usr/bin/createwsjbash.bash
chmod 4755 /usr/bin/createplistbash.bash
chmod 4755 /usr/bin/updatebash.bash
chmod 4755 /usr/bin/stopbash.bash
chmod 4755 /usr/bin/startbash.bash
chmod 4755 /usr/bin/restartbash.bash
chmod 4755 /usr/bin/statusbash.bash
chmod 4755 /usr/bin/rebootbash.bash
chmod 4755 /usr/bin/lockbash.bash
chmod 4755 /usr/bin/trashbash.bash
chmod 4755 /usr/bin/updatewcbash.bash
chmod 4755 /usr/bin/pmsscanbash.bash
chmod 4755 /usr/bin/shutdownbash.bash
chmod 4755 /usr/bin/sleepbash.bash
chmod 4755 /usr/bin/itunesbash.bash
chmod 4755 /usr/bin/quititunesbash.bash
chmod 4755 /usr/bin/logbash.bash
chmod 4755 /usr/bin/whobash.bash
chmod 4755 /usr/bin/wakebash.bash
chmod 4755 /usr/bin/tvbash.bash
chmod 400 /etc/sudoers

echo WebConnect has been updated. Refresh your browser if no icons appear.
