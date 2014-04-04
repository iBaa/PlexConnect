#!/bin/bash

## navigate to update folder
cd /applications/plexconnect/update/osx

cp -R Gradient /library/webserver/documents
chmod 777 /library/webserver/documents/gradient/ *.*
