#!/bin/bash

## find update/OSX path
cd __DEFAULTPATH__
InstallerPath=${PWD}

## find PlexConnect main path
cd ../..
PlexConnectPath=${PWD}

## go back to InstallerPath
cd update/OSX

## Copy com.plex.plexconnect.auto.plist
cp com.plex.plexconnect.auto.plist /Library/LaunchDaemons

## create autostart plist for next boot
echo 'Installing PlexConnect...'

## change ownership and permissions of the plist file to make it launchctl compatible
chown root /Library/LaunchDaemons/com.plex.plexconnect.auto.plist
chmod 644 /Library/LaunchDaemons/com.plex.plexconnect.auto.plist

## start PlexConnect for this session
echo 'Enabled auto updates for PlexConnect...'

## launch the plist so that we can use it without a reboot
launchctl load /Library/LaunchDaemons/com.plex.plexconnect.auto.plist

## wait a couple seconds to allow PlexConnect to load
sleep 2

## display the running status of PlexConnect
#./PlexConnect_daemon.bash status
launchctl list | grep com.plex.plexconnect.auto
