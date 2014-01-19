#!/bin/bash

## save path to installer files
cd "$( cd "$( dirname "$0" )" && pwd )"
InstallerPath=${PWD}

## find PlexConnect main path
cd ../..
PlexConnectPath=${PWD}

## go back to InstallerPath
cd update/OSX

## copy files to /usr.bin for system wide access
cp createcert.bash /usr/bin
cp createplist.bash /usr/bin
cp createplist2.bash /usr/bin
cp update.bash /usr/bin
cp update2.bash /usr/bin
cp stop.bash /usr/bin
cp stop2.bash /usr/bin
cp start.bash /usr/bin
cp start2.bash /usr/bin
cp restart.bash /usr/bin
cp restart2.bash /usr/bin

## replace __INSTALLERPATH__ in default createcert.bash
## save directly to the /usr/bin folder
sed -e "s/__INSTALLERPATH__/${InstallerPath//\//\\/}/" "${InstallerPath}/createcert.bash" > /usr/bin/createcert.bash

## replace __DEFAULTPATH__ in default createplist.bash
## save directly to the /usr/bin folder
sed -e "s/__DEFAULTPATH__/${InstallerPath//\//\\/}/" "${InstallerPath}/createplist.bash" > /usr/bin/createplist.bash

## replace __DEFAULTPATH__ in default createplist2.bash
## save directly to the /usr/bin folder
sed -e "s/__DEFAULTPATH__/${InstallerPath//\//\\/}/" "${InstallerPath}/createplist2.bash" > /usr/bin/createplist2.bash

## replace __INSTALLERPATH__, __USERNAME__in default update.bash
## save directly to the /usr/bin folder
sed -e "s/__INSTALLERPATH__/${InstallerPath//\//\\/}/;s/__USERNAME__/${SUDO_USER}/" "${InstallerPath}/update.bash" > /usr/bin/update.bash

## replace __INSTALLERPATH__, __USERNAME__in default update2.bash
## save directly to the /usr/bin folder
sed -e "s/__INSTALLERPATH__/${InstallerPath//\//\\/}/;s/__USERNAME__/${SUDO_USER}/" "${InstallerPath}/update2.bash" > /usr/bin/update2.bash

## fix permissions
chmod +x /usr/bin/createcert.bash
chmod +x /usr/bin/createplist.bash
chmod +x /usr/bin/createplist2.bash
chmod +x /usr/bin/update.bash
chmod +x /usr/bin/update2.bash
chmod +x /usr/bin/stop.bash
chmod +x /usr/bin/stop2.bash
chmod +x /usr/bin/start.bash
chmod +x /usr/bin/start2.bash
chmod +x /usr/bin/restart.bash
chmod +x /usr/bin/restart2.bash

## check for git and install if needed
git

## warn user to install git prior to updates
echo IF YOU CANCELED THE INSTALLATION OF GIT RERUN THIS SCRIPT. DO NOT CONTINUE UNTIL GIT IS INSTALLED YOU HAVE BEEN WARNED!
echo PROCEED ONLY IF YOU INSTALLED GIT PRIOR
