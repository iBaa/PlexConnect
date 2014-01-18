#!/bin/bash

## create autostart plist for next boot
echo 'Installing PlexConnect...'

## change ownership and permissions of the plist file to make it launchctl compatible
chown root /Library/LaunchDaemons/com.plex.plexconnect.bash.plist
chmod 644 /Library/LaunchDaemons/com.plex.plexconnect.bash.plist

## start PlexConnect for this session
echo 'Starting PlexConnect...'

## launch the plist so that we can use it without a reboot
launchctl load /Library/LaunchDaemons/com.plex.plexconnect.bash.plist

## wait a couple seconds to allow PlexConnect to load
sleep 2

## display the running status of PlexConnect
#./PlexConnect_daemon.bash status
launchctl list | grep com.plex.plexconnect.bash
