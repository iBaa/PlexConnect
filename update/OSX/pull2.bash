#!/bin/bash

mkdir /Applications/onlytemp
cd /applications/onlytemp
git clone https://github.com/wahlmanj/PlexConnect.git
cp -R /applications/onlytemp/plexconnect/update/osx/* /applications/plexconnect/update/osx
rm -R /applications/onlytemp
