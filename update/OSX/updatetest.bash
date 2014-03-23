#!/bin/bash

cd /applications/plexconnect
git fetch origin
reslog=$(git log HEAD..origin/master --oneline)
if [[ "${reslog}" != "" ]] ; then
git pull
