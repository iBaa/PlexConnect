#!/bin/bash

## update status
echo 'Stopping PlexConnect...'

## unload plexconnect from launchctl to avoid database errors
cd /library/launchdaemons
launchctl unload com.plex.plexconnect.bash.plist

## find PlexConnect main path
cd __INSTALLERPATH__
cd ../..

## display the running status of PlexConnect
launchctl list | grep com.plex.plexconnect.bash
