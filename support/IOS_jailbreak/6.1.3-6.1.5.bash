#!/bin/bash

#
# OSX PlexConnect startup script
#

#!/bin/bash
until wget -q -O - http://www.google.com | grep Lucky > /dev/null; do
sleep 10
done
exec $1&

cd /Applications/PlexConnect
./PlexConnect.py
