#!/bin/bash

export PATH=$PATH:/usr/local/git/bin/

## update status
echo 'Stopping PlexConnect...'

## unload plexconnect from launchctl to avoid database errors
cd /library/launchdaemons
launchctl unload com.plex.plexconnect.bash.plist

## find PlexConnect main path
cd __INSTALLERPATH__
cd ../..

## change permissions of .git so update.bash can be ran without su
chown -R __USERNAME__ .git

## update status
echo 'Updating PlexConnect...'

## get update
git pull

## wait a couple seconds to allow PlexConnect to update
sleep 3

## update status
echo 'Starting PlexConnect...'

## load plexconnect into launchctl after completed update
cd /library/launchdaemons
launchctl load com.plex.plexconnect.bash.plist

## wait a couple seconds to allow PlexConnect to load
sleep 2

## display the running status of PlexConnect
launchctl list | grep com.plex.plexconnect.bash

## Display PlexConnect log
FILE="/applications/plexconnect/plexconnect.log"
echo "*** File - $FILE contents ***"
cat $FILE
