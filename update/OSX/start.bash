#!/bin/bash

## update status
echo 'Starting PlexConnect...'

## unload plexconnect from launchctl to avoid database errors
cd /library/launchdaemons
launchctl load com.plex.plexconnect.bash.plist

## display the running status of PlexConnect
launchctl list | grep com.plex.plexconnect.bash

##display log
tail -f /applications/plexconnect/plexconnect.log
