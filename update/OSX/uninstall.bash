#!/bin/bash

## stop and unload PlexConnect
stop.bash

## Remove Openconnect and WebConnect scripts
rm /Library/Launchdaemons/com.plex.plexconnect.bash.plist
rm /Library/WebServer/CGI-Executables/bash.cgi
rm  /usr/bin/createcert.bash
rm  /usr/bin/createplist.bash
rm  /usr/bin/update.bash
rm  /usr/bin/stop.bash
rm  /usr/bin/start.bash
rm  /usr/bin/restart.bash
rm  /usr/bin/webconnect.bash
