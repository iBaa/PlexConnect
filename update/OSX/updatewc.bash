#!/bin/bash

export PATH=$PATH:/usr/local/git/bin/
mkdir /Applications/onlytemp
cd /applications/onlytemp
git clone https://github.com/wahlmanj/PlexConnect.git
cp -R /applications/onlytemp/plexconnect/update/osx/* /applications/plexconnect/update/osx
rm -R /applications/onlytemp
cd /
cd /applications/plexconnect/update/osx
./installwc.bash
./webconnect.bash
