#!/bin/bash

cd /Library/LaunchDaemons
chown root:wheel *.plist
chmod 644 *.plist
launchctl load *.plist
