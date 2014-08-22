stop.bash
cp /Applications/PlexConnect/update/OSX/WebServer.py /Applications/PlexConnect
cp /Applications/PlexConnect/update/OSX/DNSServer.py /Applications/PlexConnect
cp /Applications/PlexConnect/update/OSX/icon@1080.png /Applications/PlexConnect/assets/thumbnails
cp /Applications/PlexConnect/update/OSX/icon@720.png /Applications/PlexConnect/assets/thumbnails
sleep 8
start.bash
echo 'Custom Plex icon ready to upload to aTV'
