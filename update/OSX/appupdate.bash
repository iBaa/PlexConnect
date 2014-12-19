#!/bin/bash

cd /Applications/OpenPlex
export PATH=/usr/local/git/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH
git remote update
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse @{u})
BASE=$(git merge-base @ @{u})

if [ $LOCAL = $REMOTE ]; then
    echo "Up-to-date"
elif [ $LOCAL = $BASE ]; then
    echo "Need to pull"
elif [ $REMOTE = $BASE ]; then
    echo "Need to push"
else
    echo "Diverged"
fi
