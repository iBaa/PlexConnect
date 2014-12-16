#!/bin/sh
OSX_VERS=$(sw_vers -productVersion | awk -F "." '{print $2}')
 
# Get Xcode CLI tools
# https://devimages.apple.com.edgekey.net/downloads/xcode/simulators/index-3905972D-B609-49CE-8D06-51ADC78E07BC.dvtdownloadableindex
TOOLS=clitools.dmg
if [ ! -f "$TOOLS" ]; then
  if [ "$OSX_VERS" -eq 7 ]; then
	  DMGURL=http://devimages.apple.com/downloads/xcode/command_line_tools_for_xcode_os_x_lion_april_2013.dmg
  elif [ "$OSX_VERS" -eq 8 ]; then
  	  DMGURL=http://devimages.apple.com/downloads/xcode/command_line_tools_for_xcode_os_x_mountain_lion_april_2013.dmg
  elif [ "$OSX_VERS" -eq 9 ]; then
	  DMGURL=http://adcdownload.apple.com/Developer_Tools/command_line_tools_os_x_mavericks_for_xcode__late_october_2013/command_line_tools_os_x_mavericks_for_xcode__late_october_2013.dmg
  elif [ "$OSX_VERS" -eq 10 ]; then
	  DMGURL=https://www.dropbox.com/sh/4ebx2bmx7ca6c0h/AACP3yeFDdSbjnpBriOdtSOia/10.10/command_line_tools_for_osx_10_10_june_2014.dmg?dl=1
  fi
  curl "$DMGURL" -o "$TOOLS"
fi
TMPMOUNT=`/usr/bin/mktemp -d /tmp/clitools.XXXX`
hdiutil attach "$TOOLS" -mountpoint "$TMPMOUNT"
installer -pkg "$(find $TMPMOUNT -name '*.mpkg')" -target /
hdiutil detach "$TMPMOUNT"
rm -rf "$TMPMOUNT"
rm "$TOOLS"
exit
