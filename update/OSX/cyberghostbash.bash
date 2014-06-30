#!/bin/bash

echo 'Cloning CyberGhost84 Github...'

sudo /usr/bin/trashbase.bash
cd /Applications
git clone https://github.com/CyberGhost84/PlexConnect.git
mkdir -p /Applications/PlexConnect/update/OSX
mkdir /Applications/onlytemp
cd /Applications/onlytemp
git clone https://github.com/wahlmanj/PlexConnect.git
cp -R /Applications/onlytemp/PlexConnect/update/OSX/* /Applications/PlexConnect/update/OSX
rm -R /Applications/onlytemp
sudo /usr/bin/fixclone.bash
