#!/bin/bash

echo 'Cloning Wahlmanj Github...'

cd /Applications
git clone https://github.com/wahlmanj/PlexConnect.git
sudo /usr/bin/fixclone.bash
