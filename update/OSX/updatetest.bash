#!/bin/bash

export PATH=$PATH:/usr/local/git/bin/
 
# fetch changes, git stores them in FETCH_HEAD
git fetch
 
# check for remote changes in origin repository
newUpdatesAvailable=`git diff HEAD FETCH_HEAD`
if [ "$newUpdatesAvailable" != "" ]
then

## get update
git pull

else
        echo "no updates available"
fi
