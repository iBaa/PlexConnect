#!/usr/bin/python
# This should be run as sudo.

import os

plist_template = """
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN" 
	"http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>Label</key>
	<string>com.plex.plexconnect</string>
	<key>WorkingDirectory</key>
	<string>{dir}</string>
	<key>ProgramArguments</key>
	<array>
		<string>{dir}/PlexConnect.py</string>
	</array>
	<key>RunAtLoad</key>
	<true/>
	<key>KeepAlive</key>
	<true/>
</dict>
</plist>
"""

install_dir = os.path.dirname(os.path.realpath(__file__))
plist = plist_template.format(dir = install_dir).strip()

f = open('/Library/LaunchDaemons/com.plex.plexconnect.plist','w')
f.write(plist)
f.close

print "/Library/LaunchDaemons/com.plex.plexconnect.plist has now been configured."
print "To install PlexConnect so it runs on system startup, do:"
print "sudo launchctl load /Library/LaunchDaemons/com.plex.plexconnect.plist"
print "sudo launchctl start com.plex.plexconnect"
