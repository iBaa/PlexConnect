#!/bin/bash

cd /applications/plexconnect
if ! git --git-dir="/dir/.git" diff --quiet
then
    git pull
fi
