#!/bin/bash

## save path to installer files
cd "$( cd "$( dirname "$0" )" && pwd )"
InstallerPath=${PWD}

## find PlexConnect main path
cd ../..
PlexConnectPath=${PWD}

## go back to InstallerPath
cd update/OSX
DefaultPath=${PWD}

#current user
whoami=${USER}

## copy files to /usr/bin for system wide access
cp createcert.bash /usr/bin
cp createplist.bash /usr/bin
cp stop.bash /usr/bin
cp start.bash /usr/bin
cp restart.bash /usr/bin
cp websharing.bash /usr/bin

## replace __INSTALLERPATH__ in default createcert.bash
## save directly to the /usr/bin folder
sed -e "s/__INSTALLERPATH__/${InstallerPath//\//\\/}/" "${InstallerPath}/createcert.bash" > /usr/bin/createcert.bash

## replace __DEFAULTPATH__ in default createplist.bash
## save directly to the /usr/bin folder
sed -e "s/__DEFAULTPATH__/${InstallerPath//\//\\/}/" "${InstallerPath}/createplist.bash" > /usr/bin/createplist.bash

## replace __INSTALLERPATH__, __USERNAME__in default update.bash
## save directly to the /usr/bin folder
sed -e "s/__INSTALLERPATH__/${InstallerPath//\//\\/}/;s/__USERNAME__/$whoami/" "${DefaultPath}/update.bash" > /usr/bin/update.bash

## fix permissions
chmod +x /applications/plexconnect/update/osx/plexconnect.bash
chmod +x /usr/bin/createcert.bash
chmod +x /usr/bin/update.bash
chmod +x /usr/bin/stop.bash
chmod +x /usr/bin/start.bash
chmod +x /usr/bin/restart.bash
chmod +x /usr/bin/websharing.bash
