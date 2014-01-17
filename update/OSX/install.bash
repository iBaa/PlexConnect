#!/bin/bash

## save path to installer files
cd "$( cd "$( dirname "$0" )" && pwd )"
InstallerPath=${PWD}

## copy update.bash, createcert.bash, createplist.bash, com.plex.plexconnect.bash.plist to /usr.bin
cp update.bash /usr/bin
cp createcert.bash /usr/bin
cp createplist.bash /usr/bin
cp com.plex.plexconnect.bash.plist /usr/bin

## replace __INSTALLERPATH__, __USERNAME__in default update.bash
## save directly to the /usr/bin folder

sed -e "s/__INSTALLERPATH__/${InstallerPath//\//\\/}/;s/__USERNAME__/${SUDO_USER}/" "${InstallerPath}/update.bash" > /usr/bin/update.bash

sed -e "s/__INSTALLERPATH__/${InstallerPath//\//\\/}/" "${InstallerPath}/createcert.bash" > /usr/bin/createcert.bash

sed -e "s/__DEFAULTPATH__/${InstallerPath//\//\\/}/" "${InstallerPath}/createplist.bash" > /usr/bin/createplist.bash

## fix permissions
chmod +x /usr/bin/update.bash
chmod +x /usr/bin/createcert.bash
chmod +x /usr/bin/createplist.bash

## remove created file
rm /usr/bin/com.plex.plexconnect.bash.plist

## check for git and install if needed
git

## warn user to install git prior to updates
echo IF YOU CANCELED THE INSTALLATION OF GIT RERUN THIS SCRIPT. DO NOT CONTINUE UNTIL GIT IS INSTALLED YOU HAVE BEEN WARNED!
echo PROCEED ONLY IF YOU INSTALLED GIT PRIOR
