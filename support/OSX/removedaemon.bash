#!/bin/bash

## cd to PlexConnect main directory
cd "$( cd "$( dirname "$0" )" && pwd )"/../..

## remove autostart plist, stop processes
echo 'Uninstalling PlexConnect_deamon...'

## unload plist
launchctl unload /Library/LaunchDaemons/com.plex.plexconnect_daemon.bash.plist

## remove autostart plist from the /Library/LaunchDameons folder
rm /Library/LaunchDaemons/com.plex.plexconnect_daemon.bash.plist

## stop PlexConnect processes - should have been done by 'launchctl unload'
./PlexConnect_daemon.bash stop

## display the running status of PlexConnect
./PlexConnect_daemon.bash status
