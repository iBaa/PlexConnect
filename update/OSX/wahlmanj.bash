#!/bin/bash

trashbase.bash
cd /Applications
git clone https://github.com/wahlmanj/PlexConnect.git
chmod +x /Applications/PlexConnect/update/OSX/PlexConnect.bash
chmod +x /Applications/PlexConnect/update/OSX/shairport.bash
chmod +x /Applications/PlexConnect/update/OSX/airplay.bash

echo 'Wahlmanj cloned to /Applications/PlexConnect'
