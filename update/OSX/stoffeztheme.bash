#!/bin/bash

cd /applications/plexconnect/update/osx

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

cd /applications/plexconnect/assets/templates
xml.bash
