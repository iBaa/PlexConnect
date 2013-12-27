#!/bin/bash

#
# OSX PlexConnect startup script
#

#!/bin/bash thanks to @stonegray on kiwiirc
until ping -t 100 -c 1 8.8.8.8 > /dev/null
do
  echo "No internet, waiting!"
done
echo "Yay internet"

cd /Applications/PlexConnect
./PlexConnect.py
