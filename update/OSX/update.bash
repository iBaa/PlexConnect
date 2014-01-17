#!/bin/bash

## save path to installer files
cd "$( cd "$( dirname "$0" )" && pwd )"
InstallerPath=${PWD}

cd /library/launchdaemons
launchctl unload com.plex.plexconnect.plist
launchctl unload com.plex.plexconnect.bash.plist

## find PlexConnect main path
cd __INSTALLERPATH__
cd ../..

## change permissions of .git so update.bash can be ran without su
chown -R __USERNAME__ .git

## get update
git pull

echo 'Updating PlexConnect...'

## wait a couple seconds to allow PlexConnect to update
sleep 2

cd /library/launchdaemons
launchctl load com.plex.plexconnect.plist
launchctl load com.plex.plexconnect.bash.plist

## wait a couple seconds to allow PlexConnect to load
sleep 2

## display the running status of PlexConnect
launchctl list | grep com.plex.plexconnect.bash
