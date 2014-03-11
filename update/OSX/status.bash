#!/bin/bash

## display the running status of PlexConnect
ps axo pid,command | grep -i plexconnect

## Display PlexConnect log
FILE="/applications/plexconnect/plexconnect.log"
echo "*** File - $FILE contents ***"
cat $FILE

## Display Settings.cfg
FILE="/applications/plexconnect/settings.cfg"
echo "*** File - $FILE contents ***"
cat $FILE
