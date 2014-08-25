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



