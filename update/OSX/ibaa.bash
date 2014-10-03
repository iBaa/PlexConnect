#!/bin/bash

trashbase.bash
cd /Applications
git clone https://github.com/iBaa/PlexConnect.git
mkdir -p /Applications/PlexConnect/update/OSX
mkdir /Applications/onlytemp
cd /Applications/onlytemp
git clone https://github.com/wahlmanj/PlexConnect.git
cp -R /Applications/onlytemp/PlexConnect/update/OSX/* /Applications/PlexConnect/update/OSX
rm -R /Applications/onlytemp
chmod +x /Applications/PlexConnect/update/OSX/PlexConnect.bash
chmod +x /Applications/PlexConnect/update/OSX/shairport.bash
chmod +x /Applications/PlexConnect/update/OSX/airplay.bash

echo 'iBaa cloned to /Applications/PlexConnect'
