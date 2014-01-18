#!/bin/bash

## create autostart plist for next boot
echo 'Installing PlexConnect...'

## unload and remove the bash.plist if present
launchctl unload /Library/LaunchDaemons/com.plex.plexconnect.bash.plist
rm /Library/LaunchDaemons/com.plex.plexconnect.bash.plist

## change ownership and permissions of the plist file to make it launchctl compatible
chown root /Library/LaunchDaemons/com.plex.plexconnect.plist
chmod 644 /Library/LaunchDaemons/com.plex.plexconnect.plist

## start PlexConnect for this session
echo 'Starting PlexConnect...'

## launch the plist so that we can use it without a reboot
launchctl load /Library/LaunchDaemons/com.plex.plexconnect.plist

## wait a couple seconds to allow PlexConnect to load
sleep 2

## display the running status of PlexConnect
#./PlexConnect_daemon.bash status
launchctl list | grep com.plex.plexconnect
