#!/bin/bash

trashbase.bash
sleep 2
cd /Applications;
git clone https://github.com/iBaa/PlexConnect.git
mkdir -p /Applications/PlexConnect/update/OSX
mkdir /Applications/onlytemp
cd /Applications/onlytemp
git clone https://github.com/wahlmanj/PlexConnect.git
cp -R /Applications/onlytemp/PlexConnect/update/OSX/* /Applications/PlexConnect/update/OSX
rm -R /Applications/onlytemp

echo 'iBaa cloned to /Applications/PlexConnect'
