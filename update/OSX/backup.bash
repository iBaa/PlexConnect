#!/bin/bash

## cd to PlexConnect directory
cd /Applications/PlexConnect
PlexConnectPath=${PWD}

## cd to PlexConnect Backup directory
cd /Applications/plexconnect_BACKUP
BackupPath=${PWD}

stopbash.bash

cp /Applications/PlexConnect/assets/certificates/trailers.cer /Applications/plexconnect_BACKUP
cp /Applications/PlexConnect/assets/certificates/trailers.pem /Applications/plexconnect_BACKUP
cp /Applications/PlexConnect/assets/certificates/trailers.key /Applications/plexconnect_BACKUP
cp /Applications/PlexConnect/settings.cfg /Applications/plexconnect_BACKUP

fanartcache="${BackupPath}/fanartcache"
if [ -d "$fanartcache" ]; then
cp -R /Applications/PlexConnect/assets/fanartcache/* /Applications/plexconnect_BACKUP/fanartcache
else
mkdir /Applications/plexconnect_BACKUP/fanartcache
cp -R /Applications/PlexConnect/assets/fanartcache/* /Applications/plexconnect_BACKUP/fanartcache

fi

cp /Applications/PlexConnect/ATVSettings.cfg /Applications/plexconnect_BACKUP

customicons="${BackupPath}/flow"
if [ -d "$customicons" ]; then
cp -R /Applications/PlexConnect/assets/templates/plex/images/custom/flow/* /Applications/plexconnect_BACKUP/flow
cp -R /Applications/PlexConnect/assets/templates/plex/images/custom/top/* /Applications/plexconnect_BACKUP/top
else
mkdir /Applications/plexconnect_BACKUP/top
mkdir /Applications/plexconnect_BACKUP/flow
cp -R /Applications/PlexConnect/assets/templates/plex/images/custom/flow/* /Applications/plexconnect_BACKUP/flow
cp -R /Applications/PlexConnect/assets/templates/plex/images/custom/top/* /Applications/plexconnect_BACKUP/top

fi

stoffezicons="${PlexConnectPath}/assets/templates/Stoffez/images/Flow"
if [ -d "$stoffezicons" ]; then
cp -R /Applications/PlexConnect/assets/templates/Stoffez/images/Flow/* /Applications/plexconnect_BACKUP/flow
else
echo 'stoffez dir not found'

fi

startbash.bash

echo 'PlexConnect has been backed up'