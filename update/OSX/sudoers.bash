cd /Applications/PlexConnect/update/OSX

#current user
whoami=${USER}

sed -e "s/__USERNAME__/$whoami/" "/Applications/PlexConnect/update/OSX/sudoers" > /Applications/PlexConnect/update/OSX/sudoers2
