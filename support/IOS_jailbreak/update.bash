#!/bin/bash

export PATH=$PATH:/usr/local/git/bin/

#!/bin/bash
cd /Applications/PlexConnect
 
# fetch changes, git stores them in FETCH_HEAD
git fetch
 
# check for remote changes in origin repository
newUpdatesAvailable=`git diff HEAD FETCH_HEAD`
if [ "$newUpdatesAvailable" != "" ]
then

## update status
echo 'Stopping PlexConnect...'

## unload plexconnect from launchctl to avoid database errors
cd /Library/LaunchDaemons
launchctl unload com.plex.plexconnect.bash.plist

## find PlexConnect main path
cd /Applications/PlexConnect

## update status
echo 'Updating PlexConnect...'

## get update
git pull

## wait a couple seconds to allow PlexConnect to update
sleep 3

## update status
echo 'Starting PlexConnect...'

## load plexconnect into launchctl after completed update
cd /Library/LaunchDaemons
launchctl load com.plex.plexconnect.bash.plist

## wait a couple seconds to allow PlexConnect to load
sleep 2

## display the running status of PlexConnect
launchctl list | grep com.plex.plexconnect.bash

else
        echo 'no updates available'
fi
