#!/bin/bash

if [ ! -d "/Applications/PlexConnect" ]
then
osascript -e 'display notification "No Theme Installed..." with title "PlexConnect Status"'
else
echo 'theme installed'
fi

if grep "Shutting down" /Applications/Plexconnect/PlexConnect.log
then
osascript -e 'display notification "PlexConnect is Not Running..." with title "PlexConnect Status"'
value=$( grep -ic "Serving" /Applications/Plexconnect/PlexConnect.log )
elif if [ $value = 3 ]
then 
osascript -e 'display notification "PlexConnect is Running..." with title "PlexConnect Status"'
fi
