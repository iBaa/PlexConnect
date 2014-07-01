#!/bin/bash

echo 'Cloning Wahlmanj Github...'

sudo /usr/bin/trashbase.bash
cd /Applications
git clone https://github.com/wahlmanj/PlexConnect.git
sudo /usr/bin/fixclone.bash
