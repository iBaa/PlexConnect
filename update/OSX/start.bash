#!/bin/bash

## update status
echo 'Starting PlexConnect...'

## unload plexconnect from launchctl to avoid database errors
cd /library/launchdaemons
launchctl load com.plex.plexconnect.bash.plist

## display the running status of PlexConnect
launchctl list | grep com.plex.plexconnect.bash

Allow log to refresh
Sleep 3

## Display PlexConnect log
FILE="/applications/plexconnect/plexconnect.log"
echo "*** File - $FILE contents ***"
cat $FILE
