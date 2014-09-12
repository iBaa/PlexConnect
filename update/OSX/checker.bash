#!/bin/bash


## cd to PlexConnect directory
cd /Applications/PlexConnect
PlexConnectPath=${PWD}

basedir="${PlexConnectPath}"
if [ -d "$basedir" ]
then
echo 'fanartcache dir not found'
else
osascript -e 'display notification "No Theme Installed..." with title "PlexConnect Status"'
fi

if grep "Shutting down" /Applications/Plexconnect/PlexConnect.log
then
osascript -e 'display notification "PlexConnect is Not Running..." with title "PlexConnect Status"'
else
osascript -e 'display notification "PlexConnect is Running..." with title "PlexConnect Status"'
fi
