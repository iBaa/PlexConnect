cd /Applications/PlexConnect/update/OSX

#current user
whoami=${USER}

if [ -s /usr/bin/currentuser.bash ]

then
rm /usr/bin/currentuser.bash
sed -e "s/__USER__/$whoami/" "/Applications/PlexConnect/update/OSX/currentuser.bash" > /usr/bin/currentuser.bash

else
sed -e "s/__USER__/$whoami/" "/Applications/PlexConnect/update/OSX/currentuser.bash" > /usr/bin/currentuser.bash

fi
