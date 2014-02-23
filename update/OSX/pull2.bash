#!/bin/bash

export PATH=$PATH:/usr/local/git/bin/
if [ -d "/applications/onlytemp" ]
then
    echo "Directory /path/to/dir exists."
else
mkdir /Applications/onlytemp
cd /applications/onlytemp
git clone https://github.com/wahlmanj/PlexConnect.git
cp -R /applications/onlytemp/plexconnect/update/osx/* /applications/plexconnect/update/osx
rm -R /applications/onlytemp
fi
