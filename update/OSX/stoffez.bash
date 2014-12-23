#!/bin/bash

export PATH=/usr/local/git/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH
trashbase.bash
cd /Applications
git clone https://github.com/stoffez/PlexConnect.git
mkdir -p /Applications/PlexConnect/update/OSX
mkdir /Applications/onlytemp
cd /Applications/onlytemp
git clone https://github.com/wahlmanj/PlexConnect.git
cp -R /Applications/onlytemp/PlexConnect/update/OSX/* /Applications/PlexConnect/update/OSX
rm -R /Applications/onlytemp
chmod +x /Applications/PlexConnect/update/OSX/PlexConnect.bash
chmod +x /Applications/PlexConnect/update/OSX/shairport.bash
chmod +x /Applications/PlexConnect/update/OSX/airplay.bash
chmod -R ugo+rw /Applications/PlexConnect/update/OSX/

echo 'Stoffez cloned to /Applications/PlexConnect'
