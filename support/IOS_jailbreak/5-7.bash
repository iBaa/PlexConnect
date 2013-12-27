#!/bin/bash

#
# OSX PlexConnect startup script thanks to @stonegray on #kiwiirc
#

until ping -c 1 8.8.8.8 > /dev/null
do
  echo "No internet, waiting!"
done
echo "Yay internet"

#change directory & launch plexconnect

cd /Applications/PlexConnect
./PlexConnect.py
