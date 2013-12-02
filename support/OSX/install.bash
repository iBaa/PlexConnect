#!/bin/bash

## cd to PlexConnect main directory
cd "$( cd "$( dirname "$0" )" && pwd )"/../..

## check SSL certificate
file="assets/certificates/trailers.cer"
if [ -f "$file" ]; then
    echo 'SSL certificate found' 

else
    ## if not, print a reminder
    echo 'SSL certificate not found
    echo '- is it stored in a different place?'
    echo '  -> make sure to edit Settings.cfg and restart PlexConnect'
    echo '- did you already create one?
    echo '  -> run createcert.bash'

fi

## create autostart plist for next boot
echo 'Installing PlexConnect...'

## Escape the path for use with sed 
PlexConnectPath="${PWD//\//\\/}"

## replace __REPLACE_THIS_PATH__ in default com.plex.plexconnect.daemon.bash.plist
## save directly to the /Library/LaunchDameons folder
sed -e "s/__REPLACE_THIS_PATH__/${PlexConnectPath}/" ./support/OSX/com.plex.plexconnect.bash.plist > /Library/LaunchDaemons/com.plex.plexconnect.bash.plist

## change ownership and permissions of the plist file to make it launchctl compatible
chown root /Library/LaunchDaemons/com.plex.plexconnect.bash.plist
chmod 644 /Library/LaunchDaemons/com.plex.plexconnect.bash.plist

## start PlexConnect for this session
echo 'Starting PlexConnect...'

## launch the plist so that we can use it without a reboot
launchctl load /Library/LaunchDaemons/com.plex.plexconnect.bash.plist

## wait a second to allow PlexConnect to load
sleep 1

## display the running status of PlexConnect
#./PlexConnect_daemon.bash status
launchctl list | grep com.plex.plexconnect.bash
