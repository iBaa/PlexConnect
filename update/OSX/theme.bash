#!/bin/bash

cd /Applications/PlexConnect/update/OSX

## Generate xml.bash based on OSX IP Address for all .xml files
ifconfig en0|grep 'inet '|cut -d ' ' -f 2 > xml.bash
ed -s xml.bash << EOF
1
a
/g' *xml
.
1,2j
wq
EOF
ed -s xml.bash << EOF
i
sed -i '' 's/__LOCALIP__/
.
1,2j
wq
EOF
ed -s xml.bash << EOF
i
#!/bin/bash
.
wq
EOF

cp xml.bash /usr/bin

chmod +x /usr/bin/xml.bash

## future xml ip fix
cd /Applications/PlexConnect/assets/templates
xml.bash

## temporary test theme
cd /Applications/PlexConnect/update/OSX
cp Episode.xml /Applications/PlexConnect/assets/templates
cp EpisodePrePlay.xml /Applications/PlexConnect/assets/templates
cp MoviePrePlay.xml /Applications/PlexConnect/assets/templates
cp -R /Applications/PlexConnect/update/OSX/thumbnails/* /Applications/PlexConnect/assets/thumbnails

