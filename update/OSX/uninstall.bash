#!/bin/bash

## stop and unload PlexConnect
stop.bash

## Wait until plexConnect is unloaded
sleep 3

## Remove Openconnect and WebConnect scripts
rm /Library/Launchdaemons/com.plex.plexconnect.bash.plist
rm /Library/WebServer/CGI-Executables/bash.cgi
rm /usr/bin/createcert.bash
rm /usr/bin/createimovie.bash 
rm /usr/bin/createwsj.bash /usr/bin
rm /usr/bin/createplist.bash /usr/bin
rm /usr/bin/createauto.bash /usr/bin
rm /usr/bin/update.bash /usr/bin
rm /usr/bin/stop.bash /usr/bin
rm /usr/bin/start.bash /usr/bin
rm /usr/bin/restart.bash /usr/bin
rm /usr/bin/status.bash /usr/bin
rm /usr/bin/reboot.bash /usr/bin
rm /usr/bin/removecerts.bash /usr/bin
rm /usr/bin/lock.bash /usr/bin
rm /usr/bin/trash.bash /usr/bin
rm /usr/bin/webconnect.bash /usr/bin
rm /usr/bin/updatewc.bash /usr/bin
rm /usr/bin/pull.bash /usr/bin
rm /usr/bin/pull2.bash /usr/bin
rm /usr/bin/removecertsbash.bash /usr/bin
rm /usr/bin/createcertbash.bash /usr/bin
rm /usr/bin/createimoviebash.bash /usr/bin
rm /usr/bin/createwsjbash.bash /usr/bin
rm /usr/bin/createplistbash.bash /usr/bin
rm /usr/bin/updatebash.bash /usr/bin
rm /usr/bin/stopbash.bash /usr/bin
rm /usr/bin/startbash.bash /usr/bin
rm /usr/bin/restartbash.bash /usr/bin
rm /usr/bin/statusbash.bash /usr/bin
rm /usr/bin/rebootbash.bash /usr/bin
rm /usr/bin/lockbash.bash /usr/bin
rm /usr/bin/trashbash.bash /usr/bin
rm /usr/bin/updatewcbash.bash /usr/bin
rm -Rf /Applications/PlexConnect
