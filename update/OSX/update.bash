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
FILE="/Applications/PlexConnect/PlexConnect.log"
echo "*** File - $FILE contents ***"
cat $FILE

osascript -e 'tell app "OpenPlex" to display dialog "PlexConnect has been updated"'

else
        echo "no updates available"
osascript -e 'tell app "OpenPlex" to display dialog "No updates avaiable at this time"'
fi
