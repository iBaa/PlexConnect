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
cp createimovie.bash /usr/bin
cp createwsj.bash /usr/bin
cp createplist.bash /usr/bin
cp createauto.bash /usr/bin
cp update.bash /usr/bin
cp stop.bash /usr/bin
cp start.bash /usr/bin
cp restart.bash /usr/bin
cp status.bash /usr/bin
cp reboot.bash /usr/bin
co removecerts.bash/usr/bin
cp webconnect.bash /usr/bin

## replace __INSTALLERPATH__ in default createimovie.bash
## save directly to the /usr/bin folder
sed -e "s/__INSTALLERPATH__/${InstallerPath//\//\\/}/" "${InstallerPath}/createimovie.bash" > /usr/bin/createimovie.bash

## replace __INSTALLERPATH__ in default createwsj.bash
## save directly to the /usr/bin folder
sed -e "s/__INSTALLERPATH__/${InstallerPath//\//\\/}/" "${InstallerPath}/createwsj.bash" > /usr/bin/createwsj.bash

## replace __INSTALLERPATH__ in default createcert.bash
## save directly to the /usr/bin folder
sed -e "s/__INSTALLERPATH__/${InstallerPath//\//\\/}/" "${InstallerPath}/createcert.bash" > /usr/bin/createcert.bash

## replace __DEFAULTPATH__ in default createplist.bash
## save directly to the /usr/bin folder
sed -e "s/__DEFAULTPATH__/${InstallerPath//\//\\/}/" "${InstallerPath}/createplist.bash" > /usr/bin/createplist.bash

## replace __DEFAULTPATH__ in default createauto.bash
## save directly to the /usr/bin folder
sed -e "s/__DEFAULTPATH__/${InstallerPath//\//\\/}/" "${InstallerPath}/createauto.bash" > /usr/bin/createauto.bash

## replace __INSTALLERPATH__, __USERNAME__in default update.bash
## save directly to the /usr/bin folder
sed -e "s/__INSTALLERPATH__/${InstallerPath//\//\\/}/;s/__USERNAME__/${SUDO_USER}/" "${InstallerPath}/update.bash" > /usr/bin/update.bash

## replace __DEFAULTPATH__ in default webconnect.bash
## save directly to the /usr/bin folder
sed -e "s/__DEFAULTPATH__/${InstallerPath//\//\\/}/" "${InstallerPath}/webconnect.bash" > /usr/bin/webconnect.bash

## fix permissions
chmod +x /usr/bin/createcert.bash
chmod +x /usr/bin/createimovie.bash
chmod +x /usr/bin/createwsj.bash
chmod +x /usr/bin/createplist.bash
chmod +x /usr/bin/createauto.bash
chmod +x /usr/bin/update.bash
chmod +x /usr/bin/stop.bash
chmod +x /usr/bin/start.bash
chmod +x /usr/bin/restart.bash
chmod +x /usr/bin/status.bash
chmod +x /usr/bin/reboot.bash
chmod +x /usr/bin/removecerts.bash
chmod +x /usr/bin/webconnect.bash
chmod +x uninstall.bash

## check for git and prompt user to install if needed
git

## warn user to install git prior to using OpenConnect or WebConnect
echo IF YOU CANCELED THE INSTALLATION OF GIT RERUN THIS SCRIPT. DO NOT CONTINUE UNTIL GIT IS INSTALLED YOU HAVE BEEN WARNED!
echo PROCEED ONLY IF YOU INSTALLED GIT PRIOR
