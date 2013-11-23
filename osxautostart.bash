#!/bin/bash

## Escape the path for use with sed 
ourpath="${PWD//\//\\/}"

## replace __REPLACE_THIS_PATH__ in default com.plex.plexconnect.daemon.bash.plist
## and save directly to the /Library/LaunchDameons folder
sed -e "s/__REPLACE_THIS_PATH__/${ourpath}/" ./com.plex.plexconnect_daemon.bash.plist > /Library/LaunchDaemons/com.plex.plexconnect_daemon.bash.plist

## change ownership and permissions of the plist file to make it launchctl compatible
chown root /Library/LaunchDaemons/com.plex.plexconnect_daemon.bash.plist
chmod 644 /Library/LaunchDaemons/com.plex.plexconnect_daemon.bash.plist

## check to see if SSL certificate already exist
file="assets/certificates/trailers.cer"
if [ -f "$file" ]; then
	echo 'SSL Certificates already created' 

## if not, then create the required SSL certificate
else
## Comment and uncomment below to use the different ATV apps with PlexConnect
## Make sure you edit the "hosttointercept" field in Settings.cfg with the appropriate hostname listed below
 
## Trailers - hostname is trailers.apple.com
openssl req -new -nodes -newkey rsa:2048 -out ./assets/certificates/trailers.pem -keyout ./assets/certificates/trailers.key -x509 -days 7300 -subj "/C=US/CN=trailers.apple.com"
openssl x509 -in ./assets/certificates/trailers.pem -outform der -out ./assets/certificates/trailers.cer && cat ./assets/certificates/trailers.key >> ./assets/certificates/trailers.pem

## Wall Street Journal - hostname is secure.marketwatch.com
## openssl req -new -nodes -newkey rsa:2048 -out ./assets/certificates/trailers.pem -keyout ./assets/certificates/trailers.key -x509 -days 7300 -subj "/C=US/CN=secure.marketwatch.com"
## openssl x509 -in ./assets/certificates/trailers.pem -outform der -out ./assets/certificates/trailers.cer && cat ./assets/certificates/trailers.key >> ./assets/certificates/trailers.pem

## iMovie - hostname is www.icloud.com
## openssl req -new -nodes -newkey rsa:2048 -out ./assets/certificates/trailers.pem -keyout ./assets/certificates/trailers.key -x509 -days 7300 -subj "/C=US/CN=www.icloud.com"
## openssl x509 -in ./assets/certificates/trailers.pem -outform der -out ./assets/certificates/trailers.cer && cat ./assets/certificates/trailers.key >> ./assets/certificates/trailers.pem

fi

## launch the plist so that we can use it without a reboot
launchctl load /Library/LaunchDaemons/com.plex.plexconnect_daemon.bash.plist

## wait 5 seconds to allow PlexConnect to load 
sleep 5

## display the running status of PlexConnect
./PlexConnect_daemon.bash status