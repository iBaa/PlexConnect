#!/bin/bash

## goto plist
cd /applications/plexconnect/update/OSX

## Copy com.mac.lock.plist
cp com.mac.lock.plist /Library/LaunchDaemons

## change ownership and permissions of the plist file to make it launchctl compatible
chown root /Library/LaunchDaemons/com.mac.lock.plist
chmod 644 /Library/LaunchDaemons/com.mac.lock.plist
