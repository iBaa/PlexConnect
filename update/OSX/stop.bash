#!/bin/bash

## update status
echo 'Stopping PlexConnect...'

## unload plexconnect from launchctl to avoid database errors
cd /library/launchdaemons
launchctl unload com.plex.plexconnect.bash.plist

## display the running status of PlexConnect
launchctl list | grep com.plex.plexconnect.bash

## Display PlexConnect log
FILE="/applications/plexconnect/plexconnect.log"
echo "*** File - $FILE contents ***"
cat $FILE
