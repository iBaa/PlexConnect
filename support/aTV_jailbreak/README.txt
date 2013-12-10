PlexConnect on aTV (jailbroken)



Install Python on aTV
- current version: python_2.7.3-3_iphoneos-arm.deb
  see https://forums.plexapp.com/index.php/topic/72129-new-hack-running-the-plexconnect-python-script-on-your-jailbroken-atv2/?hl=%2Bnew+%2Bhack

Push PlexConnect to aTV
- SFTP into aTV and copy the complete PlexConnect directory. Eg. to /Application/PlexConnect.
- SFTP PlexConnect/support/aTV_jailbreak/Settings.cfg to PlexConnect/Settings.cfg
  overwrite the later if already there
  this bring new defaults for PlexConnect@aTV, like disabling DNSServer

/etc/hosts
- add content of PlexConnect/support/aTV_jailbreak/hosts_addon_PlexConnect to /etc/hosts
  this redirects the trailer app back to aTV itself, replacing the DNSServer
- optional: add PlexConnect/support/aTV_jailbreak/hosts_addon_preventATVUpdate
  this prevents aTV update

Install PlexConnect as daemon
- SSH into aTV
- CD into the PlexConnect directory. Eg. "cd /Application/PlexConnect"
- run "./support/aTV_jailbreak/install.bash"

Reboot

Done!



Debug PlexConnect

check processes
- "ps -ef" should find 3 Phyton/PlexConnect related processes

check launchctl
- "launchctl list | grep .plexconnect." should give "<PID>  -  com.plex.plexconnect.bach.plist"

check StdOut, StdErr
- in com.plex.plexconnect.bash.plist swap comments for StandardOutPath, StandardErrorPath payload
  dump data to real file: ./PlexConnect_stdout.log, ./PlexConnect_stderr.log
  prevent output (dflt): /dev/null
- run "./support/aTV_jailbreak/uninstall.bash"
- run "./support/aTV_jailbreak/install.bash"
