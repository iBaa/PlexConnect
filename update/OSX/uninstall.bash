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
rm /usr/bin/pmsscan.bash
rm /usr/bin/plexweb.bash
rm /usr/bin/shutdown.bash
rm /usr/bin/sleep.bash
rm /usr/bin/removecertsbash.bash
rm /usr/bin/createcertbash.bash
rm /usr/bin/createimoviebash.bash
rm /usr/bin/createwsjbash.bash
rm /usr/bin/createplistbash.bash
rm /usr/bin/updatebash.bash
rm /usr/bin/stopbash.bash
rm /usr/bin/startbash.bash
rm /usr/bin/restartbash.bash
rm /usr/bin/statusbash.bash
rm /usr/bin/rebootbash.bash
rm /usr/bin/lockbash.bash
rm /usr/bin/trashbash.bash
rm /usr/bin/updatewcbash.bash
rm /usr/bin/pmsscanbash.bash
rm /usr/bin/shutdownbash.bash
rm /usr/bin/sleepbash.bash
rm -Rf /Applications/PlexConnect
rm -Rf /Applications/OpenConnect.app

## display the running status of PlexConnect
launchctl list | grep com.plex.plexconnect.bash

## Explain uninstall has been completed
echo 'OpenConnect and WebConnect have been uninstalled if there is numerous rm commands during this script you did not install WebConnect'
