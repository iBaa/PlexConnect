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
rm /usr/bin/createwsj.bash
rm /usr/bin/createplist.bash
rm /usr/bin/createauto.bash
rm /usr/bin/update.bash
rm /usr/bin/stop.bash
rm /usr/bin/start.bash
rm /usr/bin/restart.bash
rm /usr/bin/status.bash
rm /usr/bin/reboot.bash
rm /usr/bin/removecerts.bash
rm /usr/bin/lock.bash
rm /usr/bin/trash.bash
rm /usr/bin/webconnect.bash
rm /usr/bin/updatewc.bash
rm /usr/bin/pull.bash
rm /usr/bin/pull2.bash
rm /usr/bin/removecertsbash.bash
rm /usr/bin/createcertbash.bash
rm /usr/bin/createimoviebash.bash
rm /usr/bin/createwsjbash.bash
rm /usr/bin/createplistbash.bash
rm /usr/bin/updatebash.bash
rm /usr/bin/stopbash.bash /usr/bin
rm /usr/bin/startbash.bash /usr/bin
rm /usr/bin/restartbash.bash /usr/bin
rm /usr/bin/statusbash.bash /usr/bin
rm /usr/bin/rebootbash.bash /usr/bin
rm /usr/bin/lockbash.bas
rm /usr/bin/trashbash.bash
rm /usr/bin/updatewcbash.bash
rm -Rf /Applications/PlexConnect
