#!/bin/bash

## stop and restart processes
echo 'Restarting PlexConnect...'

## unload plist
cd /Library/LaunchDaemons
launchctl unload /Library/LaunchDaemons/com.plex.plexconnect.bash.plist

## wait to allow PlexConnect to unload
Sleep 2

## load plist
launchctl load /Library/LaunchDaemons/com.plex.plexconnect.bash.plist

## wait to allow PlexConnect to load
sleep 5

## display the running status of PlexConnect
#./PlexConnect_daemon.bash status
launchctl list | grep com.plex.plexconnect.bash

## Display PlexConnect log
FILE="/applications/plexconnect/plexconnect.log"
echo "*** File - $FILE contents ***"
cat $FILE
