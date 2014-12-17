#!/bin/bash

## cd to PlexConnect directory
cd /Applications/PlexConnect
PlexConnectPath=${PWD}

## cd to PlexConnect Backup directory
cd /Applications/plexconnect_BACKUP
BackupPath=${PWD}

stopbash.bash

## allow atvsettings.cfg to generate if first clean shutdown
sleep 4

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
echo 'flow and top backup dir already present'
else
mkdir /Applications/plexconnect_BACKUP/top
mkdir /Applications/plexconnect_BACKUP/flow
echo 'flow and top backup dir created'

fi

brotusericons="${PlexConnectPath}/assets/templates/galaxy/images/flow"
if [ -d "$brotusericons" ]; then
cp -R /Applications/PlexConnect/assets/templates/plex/images/flow/* /Applications/plexconnect_BACKUP/flow
cp -R /Applications/PlexConnect/assets/templates/galaxy/images/flow/* /Applications/plexconnect_BACKUP/flow
else
echo 'brotuser flow dir not found'

fi

cyberghosticons="${PlexConnectPath}/assets/templates/plexgrey/images/custom"
if [ -d "$cyberghosticons" ]; then
cp -R /Applications/PlexConnect/assets/templates/plex/images/custom/flow/* /Applications/plexconnect_BACKUP/flow
cp -R /Applications/PlexConnect/assets/templates/plex/images/custom/top/* /Applications/plexconnect_BACKUP/top
cp -R Applications/PlexConnect/assets/templates/plexgrey/images/custom/* /Applications/plexconnect_BACKUP/flow
else 
echo 'Cyberghost flow and top dir not found'

fi

stoffezicons="${PlexConnectPath}/assets/templates/Stoffez/images/Custom"
if [ -d "$stoffezicons" ]; then
cp -R /Applications/PlexConnect/assets/templates/Stoffez/images/Custom/* /Applications/plexconnect_BACKUP/flow
else
echo 'stoffez dir not found'

fi

falcoicons="${PlexConnectPath}/assets/templates/falco953"
if [ -d "$falcoicons" ]; then
cp -R /Applications/PlexConnect/assets/thumbnails/* /Applications/plexconnect_BACKUP/flow
else
echo 'falco dir not found'

fi

startbash.bash

if [ -s /Applications/plexconnect_BACKUP ]
then
chmod -R 777 /Applications/plexconnect_BACKUP
fi

echo 'All available PlexConnect settings have been backed up'
