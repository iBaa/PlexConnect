#!/bin/bash

launchctl unload /Library/LaunchDaemons/com.plex.plexconnect.bash.plist
launchctl load /Library/LaunchDaemons/com.plex.plexconnect.bash.plist

## wait a couple seconds to allow PlexConnect to load
sleep 2

## display the running status of PlexConnect
#./PlexConnect_daemon.bash status
launchctl list | grep com.plex.plexconnect.bash

## Display PlexConnect log
FILE="/Applications/PlexConnect/PlexConnect.log"
echo "*** File - $FILE contents ***"
cat $FILE