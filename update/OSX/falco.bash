#!/bin/bash

echo 'Falco953 cloned to /Applications/PlexConnect'

sudo /usr/bin/trashbase.bash
sleep 2
cd /Applications
PATH=/usr/local/git/bin:/usr/bin:/opt/local/bin:/usr/local/bin/git export PATH
git clone https://github.com/falco953/PlexConnect.git
mkdir -p /Applications/PlexConnect/update/OSX
mkdir /Applications/onlytemp
cd /Applications/onlytemp
git clone https://github.com/wahlmanj/PlexConnect.git
cp -R /Applications/onlytemp/PlexConnect/update/OSX/* /Applications/PlexConnect/update/OSX
rm -R /Applications/onlytemp