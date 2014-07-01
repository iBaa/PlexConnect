#!/bin/bash

echo 'Wahlmanj cloned to /Applications/PlexConnect'

sudo /usr/bin/trashbase.bash
sleep 2
cd /Applications
git clone https://github.com/wahlmanj/PlexConnect.git
sudo /usr/bin/fixclone.bash
