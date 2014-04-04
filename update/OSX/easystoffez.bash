#!/bin/bash

## navigate to update folder
cd /applications/plexconnect/update/osx

cp websharing.bash /usr.bin
chmod +x /usr/bin websharing.bash

cp -R Gradient /library/webserver/documents
chmod 777 /library/webserver/documents/gradient/ *.*

rm -R /applications/plexconnect
