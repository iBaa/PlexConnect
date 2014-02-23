#!/bin/bash

export PATH=$PATH:/usr/local/git/bin/
if [ -d "/applications/plexconnect" ]
then
    echo "Directory /path/to/dir exists."
else
    cd /Applications
git clone https://github.com/iBaa/PlexConnect.git
mkdir /Applications/PlexConnect/update
mkdir /Applications/PlexConnect/update/osx
fi
