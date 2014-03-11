#!/bin/bash

echo 'This command displays your plexconnect log file'

## Display PlexConnect log
FILE="/applications/plexconnect/plexconnect.log"
echo "*** File - $FILE contents ***"
cat $FILE
