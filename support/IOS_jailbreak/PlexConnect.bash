#!/bin/bash

#
# iOS PlexConnect startup script
#

# Run in a loop until successfully connected to the internet
until wget -q -O - http://www.google.com | grep Lucky > /dev/null; do
sleep 10
done
exec $1&

# Change directory & launch plexconnect
cd /Applications/PlexConnect
./PlexConnect.py 
