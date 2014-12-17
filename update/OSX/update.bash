#!/bin/bash

## cd to PlexConnect directory
cd /Applications/PlexConnect
PlexConnectPath=${PWD}

cd /Applications/PlexConnect

export PATH=/usr/local/git/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH
 
# fetch changes, git stores them in FETCH_HEAD
git fetch
 
# check for remote changes in origin repository
newUpdatesAvailable=`git diff HEAD FETCH_HEAD`
if [ "$newUpdatesAvailable" != "" ]
then

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

## wait a couple seconds to allow PlexConnect to unload
sleep 3

## get update
git pull

## wait a couple seconds to allow PlexConnect to update
sleep 8

## update status
echo 'Starting PlexConnect...'

## load plexconnect into launchctl after completed update
cd /library/launchdaemons
launchctl load com.plex.plexconnect.bash.plist

## wait a couple seconds to allow PlexConnect to load
sleep 2
afplay /System/Library/Sounds/Glass.aiff
/usr/bin/osascript -e 'display notification "PlexConnect updated, Exit hijacked app on aTV..." with title "PlexConnect Status"'

else
echo "no updates available"
/usr/bin/osascript -e 'display notification "No Updates Available..." with title "PlexConnect Status"'
fi
