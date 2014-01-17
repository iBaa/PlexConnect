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

sleep 5

cd /library/launchdaemons
launchctl load com.plex.plexconnect.plist
launchctl load com.plex.plexconnect.bash.plist
