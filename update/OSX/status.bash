#!/bin/bash

## display the running status of PlexConnect
ps axo pid,command | grep -i plexconnect

## Display PlexConnect log
FILE="/Applications/PlexConnect/PlexConnect.log"
echo "*** File - $FILE contents ***"
cat $FILE

## Display Settings.cfg
FILE="/Applications/PlexConnect/settings.cfg"
echo "*** File - $FILE contents ***"
cat $FILE

export PATH=/usr/local/git/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH
git reset --hard
