#!/bin/bash

## stop and restart processes
echo 'Restarting PlexConnect...'

## unload plist
launchctl unload /Library/LaunchDaemons/com.plex.plexconnect.bash.plist

## wait a second to allow PlexConnect to load
sleep 1

## reload plist
launchctl load /Library/LaunchDaemons/com.plex.plexconnect.bash.plist

## display the running status of PlexConnect
#./PlexConnect_daemon.bash status
launchctl list | grep com.plex.plexconnect.bash
