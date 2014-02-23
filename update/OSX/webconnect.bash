#!/bin/bash

## install webconnect
cp bash.cgi /Library/WebServer/CGI-Executables/
chmod +x /Library/WebServer/CGI-Executables/bash.cgi

cp createcertbash.bash /usr/bin
cp createplistbash.bash /usr/bin
cp updatebash.bash /usr/bin
cp stopbash.bash /usr/bin
cp startbash.bash /usr/bin
cp restartbash.bash /usr/bin
cp statusbash.bash /usr/bin

chown root /usr/bin/createcertbash.bash 
chown root /usr/bin/createplistbash.bash
chown root /usr/bin/updatebash.bash
chown root /usr/bin/stopbash.bash
chown root /usr/bin/startbash.bash
chown root /usr/bin/restartbash.bash
chown root /usr/bin/statusbash.bash

chmod +x /usr/bin/createcertbash.bash 
chmod +x /usr/bin/createplistbash.bash
chmod +x /usr/bin/updatebash.bash
chmod +x /usr/bin/stopbash.bash
chmod +x /usr/bin/startbash.bash
chmod +x /usr/bin/restartbash.bash
chmod +x /usr/bin/statusbash.bash

chmod 4755 /usr/bin/createcertbash.bash 
chmod 4755 /usr/bin/createplistbash.bash
chmod 4755 /usr/bin/updatebash.bash
chmod 4755 /usr/bin/stopbash.bash
chmod 4755 /usr/bin/startbash.bash
chmod 4755 /usr/bin/restartbash.bash
chmod 4755 /usr/bin/statusbash.bash

## warn user to use the visudo command to edit sudoers
echo DO NOT EDIT SUDOERS WITH ANYTHING BUT THE COMMAND sudo visudo OR YOU LIKELY WILL DAMAGE YOUR SUDOERS FILE! YOU HAVE BEEN WARNED!
