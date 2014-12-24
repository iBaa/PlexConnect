#!/bin/sh
OSX_VERS=$(sw_vers -productVersion | awk -F "." '{print $2}')
 
if [ "$OSX_VERS" -eq 6 ]; then
killall OpenPlex
purgeappbash.bash
cd /Applications
curl -L https://github.com/wahlmanj/OpenPlex/raw/master/10.7/OpenPlex.zip > OpenPlex.zip
ditto -xk OpenPlex.zip /Applications
rm OpenPlex.zip
open OpenPlex.app
echo $OSX_VERS
elif [ "$OSX_VERS" -eq 7 ]; then
killall OpenPlex
purgeappbash.bash
cd /Applications
curl -L https://github.com/wahlmanj/OpenPlex/raw/master/10.7/OpenPlex.zip > OpenPlex.zip
ditto -xk OpenPlex.zip /Applications
rm OpenPlex.zip
open OpenPlex.app
echo $OSX_VERS
elif [ "$OSX_VERS" -eq 8 ]; then
killall OpenPlex
purgeappbash.bash
cd /Applications
curl -L https://github.com/wahlmanj/OpenPlex/raw/master/10.7/OpenPlex.zip > OpenPlex.zip
ditto -xk OpenPlex.zip /Applications
rm OpenPlex.zip
open OpenPlex.app
echo $OSX_VERS
elif [ "$OSX_VERS" -eq 9 ]; then
killall OpenPlex
purgeappbash.bash
cd /Applications
curl -L https://github.com/wahlmanj/OpenPlex/raw/master/10.6/OpenPlex.zip > OpenPlex.zip
ditto -xk OpenPlex.zip /Applications
rm OpenPlex.zip
open OpenPlex.app
echo $OSX_VERS
elif [ "$OSX_VERS" -eq 10 ]; then
killall OpenPlex
purgeappbash.bash
cd /Applications
curl -L https://github.com/wahlmanj/OpenPlex/raw/master/10.6/OpenPlex.zip > OpenPlex.zip
ditto -xk OpenPlex.zip /Applications
rm OpenPlex.zip
open OpenPlex.app
echo $OSX_VERS
fi

#!/bin/sh
#OSX_VERS=$(sw_vers -productVersion | awk -F "." '{print $2}')
 
# Get Xcode CLI tools
# https://devimages.apple.com.edgekey.net/downloads/xcode/simulators/index-3905972D-B609-49CE-8D06-51ADC78E07BC.dvtdownloadableindex
#TOOLS=clitools.dmg
#if [ ! -f "$TOOLS" ]; then
#    if [ "$OSX_VERS" -eq 6 ]; then
#  elif [ "$OSX_VERS" -eq 7 ]; then
#	  DMGURL=http://devimages.apple.com/downloads/xcode/command_line_tools_for_xcode_os_x_lion_april_2013.dmg
#  elif [ "$OSX_VERS" -eq 8 ]; then
#  	  DMGURL=http://devimages.apple.com/downloads/xcode/command_line_tools_for_xcode_os_x_mountain_lion_april_2013.dmg
#  elif [ "$OSX_VERS" -eq 9 ]; then
#  elif [ "$OSX_VERS" -eq 10 ]; then
#	  DMGURL=http://adcdownload.apple.com/Developer_Tools/command_line_tools_os_x_mavericks_for_xcode__late_october_2013/command_line_tools_os_x_mavericks_for_xcode__late_october_2013.dmg
#  fi
#  curl "$DMGURL" -o "$TOOLS"
# fi
# TMPMOUNT=`/usr/bin/mktemp -d /tmp/clitools.XXXX`
# hdiutil attach "$TOOLS" -mountpoint "$TMPMOUNT"
# installer -pkg "$(find $TMPMOUNT -name '*.mpkg')" -target /
# hdiutil detach "$TMPMOUNT"
# rm -rf "$TMPMOUNT"
# rm "$TOOLS"
# exit

## test 10.9 clt

## https://developer.apple.com/downloads/download.action?path=Developer_Tools/command_line_tools_os_x_10.9_for_xcode__xcode_6.1.1/commandlinetoolsosx10.9forxcode6.1.1.dmg

## TEST 10.6

## http://adcdownload.apple.com/Developer_Tools/command_line_tools_for_xcode_4.4__late_march_2012/cltools_lion_latemarch12.dmg
