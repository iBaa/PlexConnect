#!/bin/bash

export PATH=/usr/local/git/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH
mkdir /Applications/onlytemp
cd /Applications/onlytemp
git clone https://github.com/wahlmanj/PlexConnect.git
cp -R /Applications/onlytemp/PlexConnect/update/OSX/* /Applications/PlexConnect/update/OSX
rm -R /Applications/onlytemp
cd /
cd /Applications/PlexConnect/update/OSX
cp install.bash /usr/bin
chmod +x /usr/bin/install.bash
installbash.bash
