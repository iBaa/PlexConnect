#!/bin/bash

## save path to installer files
cd "$( cd "$( dirname "$0" )" && pwd )"
InstallerPath=${PWD}

## find PlexConnect main path
cd ../..
PlexConnectPath=${PWD}

## copy files to /usr.bin for system wide access
cp update.bash /usr/bin
cp update2.bash /usr/bin
cp createcert.bash /usr/bin
cp createplist.bash /usr/bin
cp createplist2.bash /usr/bin
cp com.plex.plexconnect.bash.plist /usr/bin
cp com.plex.plexconnect.plist /usr/bin

## replace __INSTALLERPATH__, __USERNAME__in default update.bash
## save directly to the /usr/bin folder
sed -e "s/__INSTALLERPATH__/${InstallerPath//\//\\/}/;s/__USERNAME__/${SUDO_USER}/" "${InstallerPath}/update.bash" > /usr/bin/update.bash

## replace __INSTALLERPATH__ in default createcert.bash
## save directly to the /usr/bin folder
sed -e "s/__INSTALLERPATH__/${InstallerPath//\//\\/}/" "${InstallerPath}/createcert.bash" > /usr/bin/createcert.bash

## replace __INSTALLERPATH__, __PLEXCONNECTPATH__ in default com.plex.plexconnect.daemon.bash.plist
## save directly to the /Library/LaunchDameons folder
sed -e "s/__INSTALLERPATH__/${InstallerPath//\//\\/}/;s/__PLEXCONNECTPATH__/${PlexConnectPath//\//\\/}/" "${InstallerPath}/com.plex.plexconnect.bash.plist" > /Library/LaunchDaemons/com.plex.plexconnect.bash.plist

## replace __INSTALLERPATH__, __PLEXCONNECTPATH__ in default com.plex.plexconnect.daemon.bash.plist
## save directly to the /Library/LaunchDameons folder
sed -e "s/__PLEXCONNECTPATH__/${PlexConnectPath//\//\\/}/" "${InstallerPath}/com.plex.plexconnect.plist" > /Library/LaunchDaemons/com.plex.plexconnect.plist

## fix permissions
chmod +x /usr/bin/update.bash
chmod +x /usr/bin/update2.bash
chmod +x /usr/bin/createcert.bash
chmod +x /usr/bin/createplist.bash
chmod +x /usr/bin/createplist2.bash

## check for git and install if needed
git

## warn user to install git prior to updates
echo IF YOU CANCELED THE INSTALLATION OF GIT RERUN THIS SCRIPT. DO NOT CONTINUE UNTIL GIT IS INSTALLED YOU HAVE BEEN WARNED!
echo PROCEED ONLY IF YOU INSTALLED GIT PRIOR
