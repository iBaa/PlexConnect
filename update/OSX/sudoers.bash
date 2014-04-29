cd /applications/plexconnect/update/osx

#current user
whoami=${USER}

sed -e "s/__USERNAME__/$whoami/" "/applications/plexconnect/update/osx/sudoers" > /applications/plexconnect/update/osx/sudoers2
