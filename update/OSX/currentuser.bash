sed -e "s/__USERNAME__/__USER__/" "/Applications/PlexConnect/update/OSX/sudoers" > /etc/sudoers3
chmod 440 /etc/sudoers3
