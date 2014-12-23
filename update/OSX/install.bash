#!/bin/bash

## save path to installer files
## cd "$( cd "$( dirname "$0" )" && pwd )"
cd /Applications/PlexConnect/update/OSX
InstallerPath=${PWD}

## find PlexConnect main path
cd ../..
PlexConnectPath=${PWD}

## go back to InstallerPath
cd update/OSX
DefaultPath=${PWD}

#current user
whoami=${USER}

## Generate wcios.bash based on OSX IP Address for webconnect.cgi
ifconfig | grep "inet " | grep -v 127.0.0.1 | cut -d\  -f2 > wcios.bash
ed -s wcios.bash << EOF
1
a
:1234\/cgi-bin\/ios.cgi/g' webconnect.cgi
.
1,2j
wq
EOF
ed -s wcios.bash << EOF
i
sed -i '' 's/__IOS__/http:\/\/
.
1,2j
wq
EOF
ed -s wcios.bash << EOF
i
cd /Library/WebServer/CGI-Executables
.
wq
EOF

## Generate wclist.bash based on OSX IP Address for webconnect.cgi
ifconfig | grep "inet " | grep -v 127.0.0.1 | cut -d\  -f2 > wclist.bash
ed -s wclist.bash << EOF
1
a
:1234\/cgi-bin\/list.cgi/g' webconnect.cgi
.
1,2j
wq
EOF
ed -s wclist.bash << EOF
i
sed -i '' 's/__LIST__/http:\/\/
.
1,2j
wq
EOF
ed -s wclist.bash << EOF
i
cd /Library/WebServer/CGI-Executables
.
wq
EOF

## Generate wcopenplex.bash based on OSX IP Address for webconnect.cgi
ifconfig | grep "inet " | grep -v 127.0.0.1 | cut -d\  -f2 > wcopenplex.bash
ed -s wcopenplex.bash << EOF
1
a
:1234\/cgi-bin\/openplex.cgi/g' webconnect.cgi
.
1,2j
wq
EOF
ed -s wcopenplex.bash << EOF
i
sed -i '' 's/__OPENPLEX__/http:\/\/
.
1,2j
wq
EOF
ed -s wcopenplex.bash << EOF
i
cd /Library/WebServer/CGI-Executables
.
wq
EOF

## Generate wcdefault.bash based on OSX IP Address for webconnect.cgi
ifconfig | grep "inet " | grep -v 127.0.0.1 | cut -d\  -f2 > wcdefault.bash
ed -s wcdefault.bash << EOF
1
a
:1234\/cgi-bin\/bash.cgi/g' webconnect.cgi
.
1,2j
wq
EOF
ed -s wcdefault.bash << EOF
i
sed -i '' 's/__DEFAULT__/http:\/\/
.
1,2j
wq
EOF
ed -s wcdefault.bash << EOF
i
cd /Library/WebServer/CGI-Executables
.
wq
EOF

## Generate wcinstaller.bash based on OSX IP Address for webconnect.cgi
ifconfig | grep "inet " | grep -v 127.0.0.1 | cut -d\  -f2 > wcinstaller.bash
ed -s wcinstaller.bash << EOF
1
a
:1234\/cgi-bin\/installer.cgi/g' webconnect.cgi
.
1,2j
wq
EOF
ed -s wcinstaller.bash << EOF
i
sed -i '' 's/__INSTALLER__/http:\/\/
.
1,2j
wq
EOF
ed -s wcinstaller.bash << EOF
i
cd /Library/WebServer/CGI-Executables
.
wq
EOF

## Generate plexweb.bash based on OSX IP Address for bash.cgi
ifconfig | grep "inet " | grep -v 127.0.0.1 | cut -d\  -f2 > plexweb.bash
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
cd /Library/WebServer/CGI-Executables
.
wq
EOF

## Generate plexwebios.bash based on OSX IP Address for ios.cgi
ifconfig | grep "inet " | grep -v 127.0.0.1 | cut -d\  -f2 > plexwebios.bash
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
cd /Library/WebServer/CGI-Executables
.
wq
EOF

## Generate plexweblist.bash based on OSX IP Address for list.cgi
ifconfig | grep "inet " | grep -v 127.0.0.1 | cut -d\  -f2 > plexweblist.bash
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
cd /Library/WebServer/CGI-Executables
.
wq
EOF

## Generate PlexWebWan.bash based on Wan IP Address for bash.cgi
curl icanhazip.com > plexwebwan.bash
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
cd /Library/WebServer/CGI-Executables
.
wq
EOF

## Generate plexwebioswan.bash based on Wan IP Address for ios.cgi
curl icanhazip.com > plexwebioswan.bash
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
cd /Library/WebServer/CGI-Executables
.
wq
EOF

## Generate plexweblistwan.bash based on Wan IP Address for list.cgi
curl icanhazip.com > plexweblistwan.bash
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
cd /Library/WebServer/CGI-Executables
.
wq
EOF

## Generate xml.bash based on OSX IP Address for all .xml files
ifconfig | grep "inet " | grep -v 127.0.0.1 | cut -d\  -f2 > xml.bash
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

## Fixes for various options
cp -R GradientTV /Library/WebServer/Documents
cp -R GradientMovies /Library/WebServer/Documents
chmod -R 0777 /Library/WebServer/Documents/GradientTV/ *.*
chmod -R 0777 /Library/WebServer/Documents/GradientMovies/ *.*
cp bash.cgi /Library/WebServer/CGI-Executables/
cp ios.cgi /Library/WebServer/CGI-Executables/
cp list.cgi /Library/WebServer/CGI-Executables/
cp openplex.cgi /Library/WebServer/CGI-Executables/
cp installer.cgi /Library/WebServer/CGI-Executables/
cp webconnect.cgi /Library/WebServer/CGI-Executables/
chmod +x /Library/WebServer/CGI-Executables/bash.cgi
chmod +x /Library/WebServer/CGI-Executables/ios.cgi
chmod +x /Library/WebServer/CGI-Executables/list.cgi
chmod +x /Library/WebServer/CGI-Executables/installer.cgi
chmod +x /Library/WebServer/CGI-Executables/openplex.cgi
chmod +x /Library/WebServer/CGI-Executables/webconnect.cgi
chmod +x /Applications/PlexConnect/update/OSX/storefront.bash

## copy files to /usr/bin for system wide access
cp hairtunes.bash /usr/bin
cp mod.bash /usr/bin
cp quit.bash /usr/bin
cp fixclone.bash /usr/bin
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
cp utorrent.bash /usr/bin
cp pht.bash /usr/bin
cp pms.bash /usr/bin
cp quititunes.bash /usr/bin
cp webconnect.bash /usr/bin
cp updatewc.bash /usr/bin
cp pmsscan.bash /usr/bin
cp shutdown.bash /usr/bin
cp sleep.bash /usr/bin
cp log.bash /usr/bin
cp who.bash /usr/bin
cp wake.bash /usr/bin
cp tv.bash /usr/bin
cp muteboot.bash /usr/bin
cp unmuteboot.bash /usr/bin
cp timemachine.bash /usr/bin
cp websharing.bash /usr/bin
cp wclist.bash /usr/bin
cp wcinstaller.bash /usr/bin
cp wcios.bash /usr/bin
cp wcdefault.bash /usr/bin
cp wcopenplex.bash /usr/bin
cp wclistbash.bash /usr/bin
cp wcinstallerbash.bash /usr/bin
cp wciosbash.bash /usr/bin
cp wcdefaultbash.bash /usr/bin
cp wcopenplexbash.bash /usr/bin
cp plexweb.bash /usr/bin
cp plexwebwan.bash /usr/bin
cp plexweblist.bash /usr/bin
cp plexwebios.bash /usr/bin
cp plexwebioswan.bash /usr/bin
cp plexweblistwan.bash /usr/bin
cp plexwebbash.bash /usr/bin
cp plexwebwanbash.bash /usr/bin
cp plexweblistbash.bash /usr/bin
cp plexwebiosbash.bash /usr/bin
cp plexwebioswanbash.bash /usr/bin
cp plexweblistwanbash.bash /usr/bin
cp quit /usr/bin
cp hide /usr/bin
cp show /usr/bin
cp hide.bash /usr/bin
cp show.bash /usr/bin
cp xml.bash /usr/bin
cp auto.bash /usr/bin
cp pillow.bash /usr/bin
cp folder.bash /usr/bin
cp sudoers.bash /usr/bin
cp restorecerts.bash /usr/bin
cp restore.bash /usr/bin
cp backup.bash /usr/bin
cp icon.bash /usr/bin
cp 10.6.bash /usr/bin
cp 10.7.bash /usr/bin
cp 10.10.bash /usr/bin
cp purgeapp.bash /usr/bin
cp purgesettings.bash /usr/bin
cp checker.bash /usr/bin
cp modbash.bash /usr/bin
cp ibaa.bash /usr/bin
cp brotuser.bash /usr/bin
cp cyberghost.bash /usr/bin
cp falco.bash /usr/bin
cp stoffez.bash /usr/bin
cp wahlmanj.bash /usr/bin
cp ibaabash.bash /usr/bin
cp cyberghostbash.bash /usr/bin
cp falcobash.bash /usr/bin
cp stoffezbash.bash /usr/bin
cp wahlmanjbash.bash /usr/bin
cp removecertsbash.bash /usr/bin
cp createcertbash.bash /usr/bin
cp createimoviebash.bash /usr/bin
cp createwsjbash.bash /usr/bin
cp createplistbash.bash /usr/bin
cp updatebash.bash /usr/bin
cp updaterbash.bash /usr/bin
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
cp utorrentbash.bash /usr/bin
cp phtbash.bash /usr/bin
cp pmsbash.bash /usr/bin
cp quititunesbash.bash /usr/bin
cp wakebash.bash /usr/bin
cp logbash.bash /usr/bin
cp whobash.bash /usr/bin
cp wol.bash /usr/bin
cp tvbash.bash /usr/bin
cp install.bash /usr/bin
cp trashbase.bash /usr/bin
cp installphp.bash /usr/bin
cp sudoersfix.bash /usr/bin
cp appupdate.bash /usr/bin
cp appupdatebash.bash /usr/bin
cp updategit.bash /usr/bin
cp updategitbash.bash /usr/bin
cp appweb.bash /usr/bin
cp appwebbash.bash /usr/bin
cp loghigh.bash /usr/bin
cp lognormal.bash /usr/bin
cp loghighbash.bash /usr/bin
cp lognormalbash.bash /usr/bin
cp timemachinebash.bash /usr/bin
cp webconnectbash.bash /usr/bin
cp websharingbash.bash /usr/bin
cp createautobash.bash /usr/bin
cp installbash.bash /usr/bin
cp installphpbash.bash /usr/bin
cp sudoersfixbash.bash /usr/bin
cp trashbasebash.bash /usr/bin
cp uninstallbash.bash /usr/bin
cp restorebash.bash /usr/bin
cp restorecertsbash.bash /usr/bin
cp backupbash.bash /usr/bin
cp iconbash.bash /usr/bin
cp 10.6bash.bash /usr/bin
cp 10.7bash.bash /usr/bin
cp 10.10bash.bash /usr/bin
cp purgeappbash.bash /usr/bin
cp purgesettingsbash.bash /usr/bin
cp checkerbash.bash /usr/bin
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

## replace __INSTALLERPATH__ in default update.bash
## save directly to the /usr/bin folder
sed -e "s/__INSTALLERPATH__/${InstallerPath//\//\\/}/" "${DefaultPath}/update.bash" > /usr/bin/update.bash

## replace __INSTALLERPATH__ in default updater.bash
## save directly to the /usr/bin folder
sed -e "s/__INSTALLERPATH__/${InstallerPath//\//\\/}/" "${DefaultPath}/updater.bash" > /usr/bin/updater.bash

## replace __DEFAULTPATH__ in default webconnect.bash
## save directly to the /usr/bin folder
sed -e "s/__DEFAULTPATH__/${InstallerPath//\//\\/}/" "${InstallerPath}/webconnect.bash" > /usr/bin/webconnect.bash

## replace __USERNAME__in default fixgit.bash
## save directly to the /usr/bin folder
sed -e "s/__USERNAME__/$whoami/" "${DefaultPath}/fixgit.bash" > /usr/bin/fixgit.bash

## fix permissions
chmod +X /usr/bin/hairtunes.bash
chmod +x /Applications/PlexConnect/update/OSX/PlexConnect.bash
chmod +x /Applications/PlexConnect/update/OSX/shairport.bash
chmod +x /Applications/PlexConnect/update/OSX/airplay.bash
chmod +x /usr/bin/mod.bash
chmod +x /usr/bin/quit.bash
chmod +x /usr/bin/fixclone.bash
chmod +x /usr/bin/createcert.bash
chmod +x /usr/bin/createimovie.bash
chmod +x /usr/bin/createwsj.bash
chmod +x /usr/bin/createplist.bash
chmod +x /usr/bin/createauto.bash
chmod +x /usr/bin/update.bash
chmod +x /usr/bin/updater.bash
chmod +x /usr/bin/updategit.bash
chmod +x /usr/bin/stop.bash
chmod +x /usr/bin/start.bash
chmod +x /usr/bin/restart.bash
chmod +x /usr/bin/status.bash
chmod +x /usr/bin/reboot.bash
chmod +x /usr/bin/removecerts.bash
chmod +x /usr/bin/lock.bash
chmod +x /usr/bin/trash.bash
chmod +x /usr/bin/itunes.bash
chmod +x /usr/bin/utorrent.bash
chmod +x /usr/bin/pht.bash
chmod +x /usr/bin/pms.bash
chmod +x /usr/bin/quititunes.bash
chmod +x /usr/bin/icon.bash
chmod +x /usr/bin/10.6.bash
chmod +x /usr/bin/10.7.bash
chmod +x /usr/bin/10.10.bash
chmod +x /usr/bin/purgeapp.bash
chmod +x /usr/bin/purgesettings.bash
chmod +x /usr/bin/checker.bash
chmod +x /usr/bin/webconnect.bash
chmod +x /usr/bin/quit
chmod +x /usr/bin/hide
chmod +x /usr/bin/show
chmod +x /usr/bin/hide.bash
chmod +x /usr/bin/show.bash
chmod +x /usr/bin/install.bash
chmod +x /usr/bin/installphp.bash
chmod +x /usr/bin/uninstall.bash
chmod +x uninstall.bash
chmod +x /usr/bin/updatewc.bash
chmod +x /usr/bin/pmsscan.bash
chmod +x /usr/bin/shutdown.bash
chmod +x /usr/bin/sleep.bash
chmod +x /usr/bin/log.bash
chmod +x /usr/bin/who.bash
chmod +x /usr/bin/wake.bash
chmod +x /usr/bin/tv.bash
chmod +x /usr/bin/wol.bash
chmod +x /usr/bin/muteboot.bash
chmod +x /usr/bin/unmuteboot.bash
chmod +x /usr/bin/timemachine.bash
chmod +x /usr/bin/websharing.bash
chmod +x /usr/bin/wclist.bash
chmod +x /usr/bin/wcinstaller.bash
chmod +x /usr/bin/wcios.bash
chmod +x /usr/bin/wcdefault.bash
chmod +x /usr/bin/wcopenplex.bash
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
chmod +x /usr/bin/trashbase.bash
chmod +x /usr/bin/sudoers.bash
chmod +x /usr/bin/modbash.bash
chmod +x /usr/bin/cyberghost.bash
chmod +x /usr/bin/ibaa.bash
chmod +x /usr/bin/brotuser.bash
chmod +x /usr/bin/stoffez.bash
chmod +x /usr/bin/falcobash.bash
chmod +x /usr/bin/wahlmanj.bash
chmod +x /usr/bin/cyberghostbash.bash
chmod +x /usr/bin/ibaabash.bash
chmod +x /usr/bin/stoffezbash.bash
chmod +x /usr/bin/falcobash.bash
chmod +x /usr/bin/wahlmanjbash.bash
chmod +x /usr/bin/createcertbash.bash
chmod +x /usr/bin/createimoviebash.bash
chmod +x /usr/bin/createwsjbash.bash
chmod +x /usr/bin/createplistbash.bash
chmod +x /usr/bin/updatebash.bash
chmod +x /usr/bin/updaterbash.bash
chmod +x /usr/bin/updategitbash.bash
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
chmod +x /usr/bin/utorrentbash.bash
chmod +x /usr/bin/phtbash.bash
chmod +x /usr/bin/pmsbash.bash
chmod +x /usr/bin/quititunesbash.bash
chmod +x /usr/bin/logbash.bash
chmod +x /usr/bin/whobash.bash
chmod +x /usr/bin/wakebash.bash
chmod +x /usr/bin/iconbash.bash
chmod +x /usr/bin/10.6bash.bash
chmod +x /usr/bin/10.7bash.bash
chmod +x /usr/bin/10.10bash.bash
chmod +x /usr/bin/purgeappbash.bash
chmod +x /usr/bin/purgesettingsbash.bash
chmod +x /usr/bin/checkerbash.bash
chmod +x /usr/bin/tvbash.bash
chmod +x /usr/bin/sudoersfix.bash
chmod +x /usr/bin/restore.bash
chmod +x /usr/bin/restorecerts.bash
chmod +x /usr/bin/backup.bash
chmod +x /usr/bin/appupdate.bash
chmod +x /usr/bin/appupdatebash.bash
chmod +x /usr/bin/appweb.bash
chmod +x /usr/bin/appwebbash.bash
chmod +x /usr/bin/loghigh.bash 
chmod +x /usr/bin/lognormal.bash
chmod +x /usr/bin/loghighbash.bash 
chmod +x /usr/bin/lognormalbash.bash
chmod +x /usr/bin/timemachinebash.bash
chmod +x /usr/bin/websharingbash.bash
chmod +x /usr/bin/webconnectbash.bash
chmod +x /usr/bin/installbash.bash
chmod +x /usr/bin/installphpbash.bash
chmod +x /usr/bin/sudoersfixbash.bash
chmod +x /usr/bin/createautobash.bash
chmod +x /usr/bin/trashbasebash.bash
chmod +x /usr/bin/uninstallbash.bash
chmod +x /usr/bin/restorebash.bash
chmod +x /usr/bin/restorecerts.bash
chmod +x /usr/bin/backupbash.bash

chmod 4755 /usr/bin/quit.bash
chmod 4755 /usr/bin/modbash.bash
chmod 4755 /usr/bin/cyberghostbash.bash
chmod 4755 /usr/bin/ibaabash.bash
chmod 4755 /usr/bin/stoffezbash.bash
chmod 4755 /usr/bin/falcobash.bash
chmod 4755 /usr/bin/wahlmanjbash.bash
chmod 4755 /usr/bin/cyberghost.bash
chmod 4755 /usr/bin/ibaa.bash
chmod 4755 /usr/bin/stoffez.bash
chmod 4755 /usr/bin/falco.bash
chmod 4755 /usr/bin/wahlmanj.bash
chmod 4755 /usr/bin/show.bash
chmod 4755 /usr/bin/hide.bash
chmod 4755 /usr/bin/removecertsbash.bash
chmod 4755 /usr/bin/createcertbash.bash
chmod 4755 /usr/bin/createimoviebash.bash
chmod 4755 /usr/bin/createwsjbash.bash
chmod 4755 /usr/bin/createplistbash.bash
chmod 4755 /usr/bin/updatebash.bash
chmod 4755 /usr/bin/updaterbash.bash
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
chmod 4755 /usr/bin/utorrentbash.bash
chmod 4755 /usr/bin/phtbash.bash
chmod 4755 /usr/bin/pmsbash.bash
chmod 4755 /usr/bin/quititunesbash.bash
chmod 4755 /usr/bin/logbash.bash
chmod 4755 /usr/bin/loghigh.bash 
chmod 4755 /usr/bin/lognormal.bash
chmod 4755 /usr/bin/appweb.bash
chmod 4755 /usr/bin/whobash.bash
chmod 4755 /usr/bin/wakebash.bash
chmod 4755 /usr/bin/tvbash.bash
chmod 4755 /usr/bin/restorebash.bash
chmod 4755 /usr/bin/restorecerts.bash
chmod 4755 /usr/bin/appupdate.bash
chmod 4755 /usr/bin/backupbash.bash
chmod 4755 /usr/bin/iconbash.bash
chmod 4755 /usr/bin/10.6bash.bash
chmod 4755 /usr/bin/10.7bash.bash
chmod 4755 /usr/bin/10.10bash.bash
chmod 4755 /usr/bin/purgeappbash.bash
chmod 4755 /usr/bin/purgesettingsbash.bash
chmod 4755 /usr/bin/checker.bash
chmod 4755 /usr/bin/timemachinebash.bash
chmod 4755 /usr/bin/websharingbash.bash
chmod 4755 /usr/bin/webconnectbash.bash
chmod 4755 /usr/bin/installbash.bash
chmod 4755 /usr/bin/installphpbash.bash
chmod 4755 /usr/bin/sudoersfixbash.bash
chmod 4755 /usr/bin/createautobash.bash
chmod 4755 /usr/bin/trashbasebash.bash
chmod 4755 /usr/bin/uninstallbash.bash

## Import LAN and WAN IP's into webconnect cgi files
plexwebbash.bash
plexwebwanbash.bash
plexwebiosbash.bash
plexwebioswanbash.bash
plexweblistbash.bash
plexweblistwanbash.bash
wclistbash.bash
wcinstallerbash.bash
wciosbash.bash
wcdefaultbash.bash
wcopenplexbash.bash

if [ -s /wclist.bash ]
then
rm /wclist.bash
fi

if [ -s /wcinstaller.bash ]
then
rm /wcinstaller.bash
fi

if [ -s /wcios.bash ]
then
rm /wcios.bash
fi

if [ -s /wcdefault.bash ]
then
rm /wcdefault.bash
fi

if [ -s /wcopenplex.bash ]
then
rm /wcopenplex.bash
fi

if [ -s /plexweb.bash ]
then
rm /plexweb.bash
fi

if [ -s /plexwebwan.bash ]
then
rm /plexwebwan.bash
fi

if [ -s /plexwebios.bash ]
then
rm /plexwebios.bash
fi

if [ -s /plexwebioswan.bash ]
then
rm /plexwebioswan.bash
fi

if [ -s /plexweblist.bash ]
then
rm /plexweblist.bash
fi

if [ -s /plexweblistwan.bash ]
then
rm /plexweblistwan.bash
fi

if [ -s /plexwebios.bash ]
then
rm /plexwebios.bash
fi

if [ -s /xml.bash ]
then
rm /xml.bash
fi

if [ -s /Applications/plexconnect_BACKUP ]
then
chmod -R 777 /Applications/plexconnect_BACKUP
fi

if [ -s /usr/bin/dark-mode ]
then
rm /usr/bin/dark-mode
fi

cd /Applications/PlexConnect/update/OSX
chmod +x clt.bash

echo 'WebConnect has been updated. Refresh your browser if no icons appear.'
