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
cp bash.cgi /Library/WebServer/CGI-Executables/
cp list.cgi /Library/WebServer/CGI-Exexutables/
chmod +x /Library/WebServer/CGI-Executables/bash.cgi

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
cp sudoers /etc
cp httpd.conf /etc/apache2

chown root /usr/bin/removecertsbash.bash
chown root /usr/bin/createcertbash.bash
chown root /usr/bin/createimoviebash.bash
chown root /usr/bin/createwsjbash.bash
chown root /usr/bin/createplistbash.bash
chown root /usr/bin/updatebash.bash
chown root /usr/bin/stopbash.bash
chown root /usr/bin/startbash.bash
chown root /usr/bin/restartbash.bash
chown root /usr/bin/statusbash.bash
chown root /usr/bin/rebootbash.bash
chown root /usr/bin/lockbash.bash
chown root /usr/bin/trashbash.bash
chown root /usr/bin/updatewcbash.bash

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
chmod 400 /etc/sudoers

echo WebConnect has been updated.
