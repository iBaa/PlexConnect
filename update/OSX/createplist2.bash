#!/bin/bash

## find update/OSX path
cd __DEFAULTPATH__
cd "$( cd "$( dirname "$0" )" && pwd )"
InstallerPath=${PWD}

## find PlexConnect main path
cd ../..
PlexConnectPath=${PWD}

## go back to InstallerPath
cd update/OSX

## Copy com.plex.plexconnect.plist
cp com.plex.plexconnect.plist /Library/LaunchDaemons

## replace __PLEXCONNECTPATH__ in default com.plex.plexconnect.plist
## save directly to the /Library/LaunchDameons folder
sed -e "s/__PLEXCONNECTPATH__/${PlexConnectPath//\//\\/}/" "${InstallerPath}/com.plex.plexconnect.plist" > /Library/LaunchDaemons/com.plex.plexconnect.plist

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
