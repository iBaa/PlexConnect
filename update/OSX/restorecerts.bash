#!/bin/bash

cp /Applications/plexconnect_BACKUP/trailers.cer /Applications/PlexConnect/assets/certificates
cp /Applications/plexconnect_BACKUP/trailers.pem /Applications/PlexConnect/assets/certificates
cp /Applications/plexconnect_BACKUP/trailers.key /Applications/PlexConnect/assets/certificates

echo 'All backup certs have been restored'
