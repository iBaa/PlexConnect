#!/bin/bash

if grep "Shutting down" /Applications/Plexconnect/PlexConnect.log
then
osascript -e 'tell app "System Events" to display dialog "PlexConnect is Not Running..."
else
osascript -e 'tell app "System Events" to display dialog "PlexConnect is Running..."
fi
