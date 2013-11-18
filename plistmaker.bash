#!/bin/bash

## Escape the path for use with sed 
ourpath="${PWD//\//\\/}"

## replace __REPLACE_THIS_PATH__ in default com.plex.plexconnect.daemon.bash.plist
## and save directly to the /Library/LaunchDameons folder
sed -e "s/__REPLACE_THIS_PATH__/${ourpath}/" ./com.plex.plexconnect_daemon.bash.plist > /Library/LaunchDaemons/com.plex.plexconnect_daemon.bash.plist

## change ownership and permissions of the plist file to make it launchctl compatible
chown root /Library/LaunchDaemons/com.plex.plexconnect_daemon.bash.plist
chmod 644 /Library/LaunchDaemons/com.plex.plexconnect_daemon.bash.plist

## create the required SSL certificates
openssl req -new -nodes -newkey rsa:2048 -out ./assets/certificates/trailers.pem -keyout ./assets/certificates/trailers.key -x509 -days 7300 -subj "/C=US/CN=trailers.apple.com"
openssl x509 -in ./assets/certificates/trailers.pem -outform der -out ./assets/certificates/trailers.cer && cat ./assets/certificates/trailers.key >> ./assets/certificates/trailers.pem

## launch the plist so that we can use it without a reboot
launchctl load /Library/LaunchDaemons/com.plex.plexconnect_daemon.bash.plist

## wait 10 seconds to allow PlexConnect to load 
sleep 10

## display the running status of PlexConnect
./PlexConnect_daemon.bash status

