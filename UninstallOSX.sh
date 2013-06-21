#!/bin/bash

sudo launchctl stop com.plex.plexconnect
sudo launchctl unload /Library/LaunchDaemons/com.plex.plexconnect.plist
sudo rm /Library/LaunchDaemons/com.plex.plexconnect.plist
