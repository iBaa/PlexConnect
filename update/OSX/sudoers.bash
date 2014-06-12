cd /Applications/PlexConnect/update/OSX

#current user
whoami=${USER}

sed -e "s/__USERNAME__/$whoami/" "/Applications/Plexconnect/update/OSX/sudoers" > /Applications/Plexconnect/update/OSX/sudoers2
