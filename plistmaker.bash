#!/bin/bash

## Escape the path for use with sed 
ourpath="${PWD//\//\\/}"

## replace __REPLACE_THIS_PATH__ in default com.plex.plexconnect.daemon.bash.plist
## and save directly to the /Library/LaunchDameons folder
sed -e "s/__REPLACE_THIS_PATH__/${ourpath}/" ./com.plex.plexconnect_daemon.bash.plist > /Library/LaunchDaemons/com.plex.plexconnect_daemon.bash.plist

## change ownership and permissions of the plist file to make it launchctl compatible
chown root /Library/LaunchDaemons/com.plex.plexconnect_daemon.bash.plist
chmod 644 /Library/LaunchDaemons/com.plex.plexconnect_daemon.bash.plist

## move plist file to the right location for it to load automatically at boot time
#mv -f ./com.plex.plexconnect_daemon.bash.plist.tmp /Library/LaunchDaemons
#mv ./com.plex.plexconnect_daemon.bash.plist.bak ./com.plex.plexconnect_daemon.bash.plist

## launch the plist so that we can use it without a reboot
launchctl load /Library/LaunchDaemons/com.plex.plexconnect_daemon.bash.plist

## wait 10 seconds to allow PlexConnect to load 
sleep 10

## display the running status of PlexConnect
./PlexConnect_daemon.bash status

