#!/bin/bash

cd /applications/plexconnext
git fetch origin
reslog=$(git log HEAD..origin/master --oneline)
if [[ "${reslog}" != "" ]] ; then
git pull
