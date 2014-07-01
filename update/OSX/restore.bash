#!/bin/bash

## cd to PlexConnect directory
cd /Applications/PlexConnect
PlexConnectPath=${PWD}

cp /Applications/plexconnect_BACKUP/ATVSettings.cfg /Applications/PlexConnect
cp /Applications/plexconnect_BACKUP/settings.cfg /Applications/PlexConnect
cp /Applications/plexconnect_BACKUP/trailers.cer /Applications/PlexConnect/assets/certificates
cp /Applications/plexconnect_BACKUP/trailers.pem /Applications/PlexConnect/assets/certificates
cp /Applications/plexconnect_BACKUP/trailers.key /Applications/PlexConnect/assets/certificates

fanartcache="${PlexConnectPath}/assets/fanartcache"
if [ -d "$fanartcache" ]; then
rm /Applications/PlexConnect/assets/fanartcache/*
cp -R /Applications/plexconnect_BACKUP/fanartcache/* /Applications/PlexConnect/assets/fanartcache
else
echo 'fanartcache dir not found'

fi

customicons="${PlexConnectPath}/assets/templates/plex/images/custom/flow"
if [ -d "$customicons" ]; then
cp -R /Applications/plexconnect_BACKUP/flow/* /Applications/PlexConnect/assets/templates/plex/images/custom/flow
cp -R /Applications/plexconnect_BACKUP/top/* /Applications/PlexConnect/assets/templates/plex/images/custom/top
else
echo 'flow and top dir not found'

fi

thumbnails="${PlexConnectPath}/assets/thumbnails"
if [ -d "$thumbnails" ]; then
cp -R /Applications/plexconnect_BACKUP/thumbnails* /Applications/PlexConnect/assets/thumbnails
else 
echo 'thumbnail dir not found'

fi

sudo /usr/bin/restart.bash
