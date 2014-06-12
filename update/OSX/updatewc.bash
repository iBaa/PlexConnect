#!/bin/bash

export PATH=$PATH:/usr/local/git/bin/
mkdir /Applications/onlytemp
cd /Applications/onlytemp
git clone https://github.com/wahlmanj/PlexConnect.git
cp -R /Applications/onlytemp/PlexConnect/update/OSX/* /Applications/PlexConnect/update/OSX
rm -R /Applications/onlytemp
cd /
cd /Applications/PlexConnect/update/OSX
cp installwc.bash /usr/bin
chmod +x /usr/bin/installwc.bash
installwc.bash
webconnect.bash
