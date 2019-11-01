#!/bin/bash

## remove autostart plist, stop processes
echo 'Uninstalling PlexConnect...'

## unload plist
launchctl unload /Library/LaunchDaemons/com.plex.plexconnect.bash.plist

## remove autostart plist from the /Library/LaunchDameons folder
rm /Library/LaunchDaemons/com.plex.plexconnect.bash.plist

## display the running status of PlexConnect
launchctl list | grep com.plex.plexconnect.bash
