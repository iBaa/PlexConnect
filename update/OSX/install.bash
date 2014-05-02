#!/bin/bash



## save path to installer files
## cd "$( cd "$( dirname "$0" )" && pwd )"
cd /applications/plexconnect/update/osx
InstallerPath=${PWD}

## find PlexConnect main path
cd ../..
PlexConnectPath=${PWD}

## go back to InstallerPath
cd update/OSX
DefaultPath=${PWD}

#current user
whoami=${USER}

## Generate plexweb.bash based on OSX IP Address for bash.cgi
ifconfig en0|grep 'inet '|cut -d ' ' -f 2 > plexweb.bash
ed -s plexweb.bash << EOF
1
a
:32400\/web\/index.html#!\/dashboard/g' bash.cgi
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

## Generate plexwebios.bash based on OSX IP Address for ios.cgi
ifconfig en0|grep 'inet '|cut -d ' ' -f 2 > plexwebios.bash
ed -s plexwebios.bash << EOF
1
a
:32400\/web\/index.html#!\/dashboard/g' ios.cgi
.
1,2j
wq
EOF
ed -s plexwebios.bash << EOF
i
sed -i '' 's/__PLEXWEB__/http:\/\/
.
1,2j
wq
EOF
ed -s plexwebios.bash << EOF
i
#!/bin/bash
.
wq
EOF

## Generate plexweblist.bash based on OSX IP Address for list.cgi
ifconfig en0|grep 'inet '|cut -d ' ' -f 2 > plexweblist.bash
ed -s plexweblist.bash << EOF
1
a
:32400\/web\/index.html#!\/dashboard/g' list.cgi
.
1,2j
wq
EOF
ed -s plexweblist.bash << EOF
i
sed -i '' 's/__PLEXWEB__/http:\/\/
.
1,2j
wq
EOF
ed -s plexweblist.bash << EOF
i
#!/bin/bash
.
wq
EOF

## Generate PlexWebWan.bash based on Wan IP Address for bash.cgi
curl ifconfig.me > plexwebwan.bash
ed -s plexwebwan.bash << EOF
1
a
:32400\/web\/index.html#!\/dashboard/g' bash.cgi
.
1,2j
wq
EOF
ed -s plexwebwan.bash << EOF
i
sed -i '' 's/__PLEXWEBWAN__/http:\/\/
.
1,2j
wq
EOF
ed -s plexwebwan.bash << EOF
i
#!/bin/bash
.
wq
EOF

## Generate plexwebioswan.bash based on Wan IP Address for ios.cgi
curl ifconfig.me > plexwebioswan.bash
ed -s plexwebioswan.bash << EOF
1
a
:32400\/web\/index.html#!\/dashboard/g' ios.cgi
.
1,2j
wq
EOF
ed -s plexwebioswan.bash << EOF
i
sed -i '' 's/__PLEXWEBWAN__/http:\/\/
.
1,2j
wq
EOF
ed -s plexwebioswan.bash << EOF
i
#!/bin/bash
.
wq
EOF

## Generate plexweblistwan.bash based on Wan IP Address for list.cgi
curl ifconfig.me > plexweblistwan.bash
ed -s plexweblistwan.bash << EOF
1
a
:32400\/web\/index.html#!\/dashboard/g' list.cgi
.
1,2j
wq
EOF
ed -s plexweblistwan.bash << EOF
i
sed -i '' 's/__PLEXWEBWAN__/http:\/\/
.
1,2j
wq
EOF
ed -s plexweblistwan.bash << EOF
i
#!/bin/bash
.
wq
EOF

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

cp -R Gradient /library/webserver/documents
chmod -R 0777 /library/webserver/documents/gradient/ *.*

## copy files to /usr/bin for system wide access
cp createcert.bash /usr/bin
cp createimovie.bash /usr/bin
cp createwsj.bash /usr/bin
cp createplist.bash /usr/bin
cp createauto.bash /usr/bin
cp stop.bash /usr/bin
cp start.bash /usr/bin
cp restart.bash /usr/bin
cp status.bash /usr/bin
cp reboot.bash /usr/bin
cp removecerts.bash /usr/bin
cp lock.bash /usr/bin
cp trash.bash /usr/bin
cp itunes.bash /usr/bin
cp quititunes.bash /usr/bin
cp webconnect.bash /usr/bin
cp updatewc.bash /usr/bin
cp pull.bash /usr/bin
cp pull2.bash /usr/bin
cp pmsscan.bash /usr/bin
cp shutdown.bash /usr/bin
cp sleep.bash /usr/bin
cp log.bash /usr/bin
cp who.bash /usr/bin
cp wake.bash /usr/bin
cp tv.bash /usr/bin
cp timemachine.bash /usr/bin
cp websharing.bash /usr/bin
cp plexweb.bash /usr/bin
cp plexwebwan.bash /usr/bin
cp plexweblist.bash /usr/bin
cp plexwebios.bash /usr/bin
cp plexwebioswan.bash /usr/bin
cp plexweblistwan.bash /usr/bin
cp quit /usr/bin
cp hide /usr/bin
cp show /usr/bin
cp xml.bash /usr/bin
cp auto.bash /usr/bin
cp pillow.bash /usr/bin
cp folder.bash /usr/bin
cp sudoers.bash /usr/bin
cp httpd.conf /etc/apache2
cp removecertsbash.bash /usr/bin
cp createcertbash.bash /usr/bin
cp createimoviebash.bash /usr/bin
cp createwsjbash.bash /usr/bin
cp createplistbash.bash /usr/bin
cp updatebash.bash /usr/bin
cp stopbash.bash /usr/bin
cp startbash.bash /usr/bin
cp restartbash.bash /usr/bin
cp statusbash.bash /usr/bin
cp rebootbash.bash /usr/bin
cp lockbash.bash /usr/bin
cp trashbash.bash /usr/bin
cp updatewcbash.bash /usr/bin
cp pmsscanbash.bash /usr/bin
cp shutdownbash.bash /usr/bin
cp sleepbash.bash /usr/bin
cp itunesbash.bash /usr/bin
cp quititunesbash.bash /usr/bin
cp wakebash.bash /usr/bin
cp logbash.bash /usr/bin
cp whobash.bash /usr/bin
cp tvbash.bash /usr/bin
cp install.bash /usr/bin
cp sudoersfix.bash /usr/bin
cp timemachinebash.bash /usr/bin
cp webconnectbash.bash /usr/bin
cp websharingbash.bash /usr/bin
cp installbash.bash /usr/bin
cp sudoersfixbash.bash /usr/bin
cp uninstallbash.bash /usr/bin
cp uninstall.bash /usr/bin


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
sed -e "s/__INSTALLERPATH__/${InstallerPath//\//\\/}/;s/__USERNAME__/$whoami/" "${DefaultPath}/update.bash" > /usr/bin/update.bash

## replace __DEFAULTPATH__ in default webconnect.bash
## save directly to the /usr/bin folder
sed -e "s/__DEFAULTPATH__/${InstallerPath//\//\\/}/" "${InstallerPath}/webconnect.bash" > /usr/bin/webconnect.bash

## replace __USERNAME__in default fixgit.bash
## save directly to the /usr/bin folder
sed -e "s/__USERNAME__/$whoami/" "${DefaultPath}/fixgit.bash" > /usr/bin/fixgit.bash

## fix permissions
chmod +x /applications/plexconnect/update/osx/plexconnect.bash
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
chmod +x /usr/bin/itunes.bash
chmod +x /usr/bin/quititunes.bash
chmod +x /usr/bin/webconnect.bash
chmod +x /usr/bin/quit
chmod +x /usr/bin/hide
chmod +x /usr/bin/show
chmod +x /usr/bin/install.bash
chmod +x /usr/bin/uninstall.bash
chmod +x uninstall.bash
chmod +x /usr/bin/updatewc.bash
chmod +x /usr/bin/pull.bash
chmod +x /usr/bin/pull2.bash
chmod +x /usr/bin/pmsscan.bash
chmod +x /usr/bin/shutdown.bash
chmod +x /usr/bin/sleep.bash
chmod +x /usr/bin/log.bash
chmod +x /usr/bin/who.bash
chmod +x /usr/bin/wake.bash
chmod +x /usr/bin/tv.bash
chmod +x /usr/bin/wol.bash
chmod +x /usr/bin/timemachine.bash
chmod +x /usr/bin/websharing.bash
chmod +x /usr/bin/plexweb.bash
chmod +x /usr/bin/plexwebwan.bash
chmod +x /usr/bin/plexweblist.bash
chmod +x /usr/bin/plexwebios.bash
chmod +x /usr/bin/plexwebioswan.bash
chmod +x /usr/bin/plexweblistwan.bash
chmod +x /usr/bin/xml.bash
chmod +x /usr/bin/fixgit.bash
chmod +x /usr/bin/auto.bash
chmod +x /usr/bin/pillow.bash
chmod +x /usr/bin/folder.bash
chmod +x /usr/bin/sudoers.bash
chmod +x /usr/bin/createcertbash.bash
chmod +x /usr/bin/createimoviebash.bash
chmod +x /usr/bin/createwsjbash.bash
chmod +x /usr/bin/createplistbash.bash
chmod +x /usr/bin/updatebash.bash
chmod +x /usr/bin/stopbash.bash
chmod +x /usr/bin/startbash.bash
chmod +x /usr/bin/restartbash.bash
chmod +x /usr/bin/statusbash.bash
chmod +x /usr/bin/rebootbash.bash
chmod +x /usr/bin/lockbash.bash
chmod +x /usr/bin/trashbash.bash
chmod +x /usr/bin/updatewcbash.bash
chmod +x /usr/bin/pmsscanbash.bash
chmod +x /usr/bin/shutdownbash.bash
chmod +x /usr/bin/sleepbash.bash
chmod +x /usr/bin/itunesbash.bash
chmod +x /usr/bin/quititunesbash.bash
chmod +x /usr/bin/logbash.bash
chmod +x /usr/bin/whobash.bashw
chmod +x /usr/bin/wakebash.bash
chmod +x /usr/bin/tvbash.bash
chmod +x /usr/bin/sudoersfix.bash
chmod +x /usr/bin/timemachinebash.bash
chmod +x /usr/bin/websharingbash.bash
chmod +x /usr/bin/webconnectbash.bash
chmod +x /usr/bin/installbash.bash
chmod +x /usr/bin/sudoersfixbash.bash
chmod +x /usr/bin/uninstallbash.bash

chmod 4755 /usr/bin/removecertsbash.bash
chmod 4755 /usr/bin/createcertbash.bash
chmod 4755 /usr/bin/createimoviebash.bash
chmod 4755 /usr/bin/createwsjbash.bash
chmod 4755 /usr/bin/createplistbash.bash
chmod 4755 /usr/bin/updatebash.bash
chmod 4755 /usr/bin/stopbash.bash
chmod 4755 /usr/bin/startbash.bash
chmod 4755 /usr/bin/restartbash.bash
chmod 4755 /usr/bin/statusbash.bash
chmod 4755 /usr/bin/rebootbash.bash
chmod 4755 /usr/bin/lockbash.bash
chmod 4755 /usr/bin/trashbash.bash
chmod 4755 /usr/bin/updatewcbash.bash
chmod 4755 /usr/bin/pmsscanbash.bash
chmod 4755 /usr/bin/shutdownbash.bash
chmod 4755 /usr/bin/sleepbash.bash
chmod 4755 /usr/bin/itunesbash.bash
chmod 4755 /usr/bin/quititunesbash.bash
chmod 4755 /usr/bin/logbash.bash
chmod 4755 /usr/bin/whobash.bash
chmod 4755 /usr/bin/wakebash.bash
chmod 4755 /usr/bin/tvbash.bash
chmod 4755 /usr/bin/timemachinebash.bash
chmod 4755 /usr/bin/websharingbash.bash
chmod 4755 /usr/bin/webconnectbash.bash
chmod 4755 /usr/bin/installbash.bash
chmod 4755 /usr/bin/sudoersfixbash.bash
chmod 4755 /usr/bin/uninstallbash.bash

## Fix ip in all xml files
cd /applications/plexconnect/assets/templates
xml.bash
