cd /Applications/PlexConnect/update/OSX

#current user
whoami=${USER}

if [ -s /Applications/PlexConnect/update/OSX/sudoers2 ]

then
rm /Applications/PlexConnect/update/OSX/sudoers2
sed -e "s/__USERNAME__/$whoami/" "/Applications/PlexConnect/update/OSX/sudoers" > /Applications/PlexConnect/update/OSX/sudoers2

else
sed -e "s/__USERNAME__/$whoami/" "/Applications/PlexConnect/update/OSX/sudoers" > /Applications/PlexConnect/update/OSX/sudoers2

fi

if [ -s /usr/bin/currentuser.bash ]

then
rm /usr/bin/currentuser.bash
sed -e "s/__USER__/$whoami/" "/Applications/PlexConnect/update/OSX/currentuser.bash" > /usr/bin/currentuser.bash

else
sed -e "s/__USER__/$whoami/" "/Applications/PlexConnect/update/OSX/currentuser.bash" > /usr/bin/currentuser.bash

fi



