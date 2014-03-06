#!/bin/bash

## save path to installer files
cd "$( cd "$( dirname "$0" )" && pwd )"
InstallerPath=${PWD}

## find PlexConnect main path
cd ../..
PlexConnectPath=${PWD}

## go back to InstallerPath
cd update/OSX

## Generate PlexWeb based on OSX IP Address
ifconfig en0|grep 'inet '|cut -d ' ' -f 2 > plexweb.bash
ed -s plexweb.bash << EOF
1
a
:32400\/web/g' bash.cgi
.
1,2j
wq
EOF
ed -s plexweb.bash << EOF
i
sed -i '' 's/__PLEXWEB__/http:\/\/
.
1,2j
wq
EOF
ed -s plexweb.bash << EOF
i
#!/bin/bash
.
wq
EOF

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
cp removecerts.bash /usr/bin
cp lock.bash /usr/bin
cp trash.bash /usr/bin
cp webconnect.bash /usr/bin
cp updatewc.bash /usr/bin
cp pull.bash /usr/bin
cp pull2.bash /usr/bin
cp pmsscan.bash /usr/bin
cp plexweb.bash /usr/bin
cp shutdown.bash /usr/bin
cp sleep.bash /usr/bin

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
chmod +x /usr/bin/lock.bash
chmod +x /usr/bin/trash.bash
chmod +x /usr/bin/webconnect.bash
chmod +x uninstall.bash
chmod +x /usr/bin/updatewc.bash
chmod +x /usr/bin/pull.bash
chmod +x /usr/bin/pull2.bash
chmod +x /usr/bin/pmsscan.bash
chmod +x /usr/bin/plexweb.bash
chmod +x /usr/bin/shutdown.bash
chmod +x /usr/bin/sleep.bash
