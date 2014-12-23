#!/bin/bash

## stop and restart processes
echo 'Restarting PlexConnect...'

## unload plist
cd /Library/LaunchDaemons
launchctl unload /Library/LaunchDaemons/com.plex.plexconnect.bash.plist

## load plist
launchctl load /Library/LaunchDaemons/com.plex.plexconnect.bash.plist

## wait to allow PlexConnect to load and allow log to refresh
Sleep 2

## display the running status of PlexConnect
#./PlexConnect_daemon.bash status
launchctl list | grep com.plex.plexconnect.bash

if [ ! -f /Applications/PlexConnect/PlexConnect.log ]
then
echo 'No log present'
else
## Display PlexConnect log
FILE="/Applications/PlexConnect/PlexConnect.log"
echo "*** File - $FILE contents ***"
cat $FILE
fi
