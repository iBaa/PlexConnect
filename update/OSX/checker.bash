#!/bin/bash

if [ ! -d "/Applications/PlexConnect" ]
then
osascript -e 'display notification "No Theme Installed..." with title "PlexConnect Status"'
else
echo 'theme installed'
fi

if grep "Shutting down" /Applications/Plexconnect/PlexConnect.log
then
afplay /System/Library/Sounds/Basso.aiff
osascript -e 'display notification "PlexConnect is Not Running..." with title "PlexConnect Status"'
fi

value=$( grep -ic "Serving\|Shutting" /Applications/PlexConnect/PlexConnect.log )
if [ $value = 3 ]
then
afplay /System/Library/Sounds/Submarine.aiff
osascript -e 'display notification "PlexConnect is Running..." with title "PlexConnect Status"'
fi

if [ ! -f /Applications/PlexConnect/assets/certificates/trailers.cer ]
then
osascript -e 'display notification "No Certs present, Choose hijack..." with title "PlexConnect Status"'
fi
