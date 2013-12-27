#!/bin/bash

#
# OSX PlexConnect startup script thanks to @stonegray on #kiwiirc
#

echo "Can I has internet?"
until ping -c 1 8.8.8.8 > /dev/null  #fixed?
do
  echo "No internet, waiting!"
done
echo "Yay internet"

#change directory & launch plexconnect

cd /Applications/PlexConnect
./PlexConnect.py
