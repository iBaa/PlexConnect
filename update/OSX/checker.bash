#!/bin/bash

if grep "Shutting down" /Applications/Plexconnect/PlexConnect.log
then
osascript -e 'display notification "PlexConnect is Not Running..." with title "PlexConnect Status"'
else
osascript -e 'display notification "PlexConnect is Running..." with title "PlexConnect Status"'
fi
