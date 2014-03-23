#!/bin/bash

cd /applications/plexconnext
git fetch origin
reslog=$(git log HEAD..origin/master --oneline)
if [[ "${reslog}" != "" ]] ; then
stop.bash
git pull
sleep 2
start.bash
