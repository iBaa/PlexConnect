#!/bin/bash

#
# OSX PlexConnect startup script thanks to @stonegray on kiwiirc
#

#!/bin/bash
until ping -W 100 -t 100 -c 1 8.8.8.8 > /dev/null 
do
  echo "No internet, waiting!"
done
echo "Yay internet"

#change directory & launch plexconnect

cd /Applications/PlexConnect
./PlexConnect.py
