#!/bin/bash

## go back to InstallerPath
cd /Applications/PlexConnect/update/OSX

## Copy wol plists to /Library/LaunchAgents
cp com.plexconnect.wake_dns.plist /Library/LaunchAgents
cp com.plexconnect.wake_pms.plist /Library/LaunchAgents
cp com.plexconnect.wake_web.plist /Library/LaunchAgents

## change ownership and permissions of the plists to make them launchctl compatible
chown root /Library/LaunchAgents/com.plexconnect.wake_dns.plist
chown root /Library/LaunchAgents/com.plexconnect.wake_pms.plist
chown root /Library/LaunchAgents/com.plexconnect.wake_web.plist
chmod 644 /Library/LaunchAgents/com.plexconnect.wake_dns.plist
chmod 644 /Library/LaunchAgents/com.plexconnect.wake_pms.plist
chmod 644 /Library/LaunchAgents/com.plexconnect.wake_web.plist

## launch the plists so that we can use them without a reboot
launchctl load /Library/LaunchAgents/com.plexconnect.wake_dns.plist
launchctl load /Library/LaunchAgents/com.plexconnect.wake_pms.plist
launchctl load /Library/LaunchAgents/com.plexconnect.wake_web.plist
