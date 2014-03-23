#!/bin/bash
cd /applications/plexconnect
if git fetch origin master &&
    [ `git rev-list HEAD...origin/master --count` != 0 ] &&
then
git pull
else
    echo 'Not updated.'
fi
