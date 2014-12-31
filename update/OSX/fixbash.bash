#!/bin/bash

if [ -s /Applications/PlexConnect/update/OSX ]
then
cd /Applications/PlexConnect/update/OSX
ed -s PlexConnect.bash << EOF
i
export PATH=/usr/local/bin:$PATH
.
wq
EOF
fi
