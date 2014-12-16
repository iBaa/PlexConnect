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
	  DMGURL=http://qd.baidupcs.com/file/b19bb382d758d995662d21dc149484c3?bkt=p2-nj-897&fid=422877698-250528-46527744964142&time=1418726215&sign=FDTAXERLB-DCb740ccc5511e5e8fedcff06b081203-kfAjPZ3DYzb1sQgqexyHIKABjIc%3D&to=qb&fm=Qin,B,U,ny&newver=1&newfm=1&flow_ver=3&sl=81723464&expires=1418728119&rt=sh&r=448629972&mlogid=1246248485&sh=1&vuk=-&vbdid=844524738&fin=command_line_tools_for_osx_mavericks_june_2014.dmg
  elif [ "$OSX_VERS" -eq 10 ]; then
	  DMGURL=http://qd.baidupcs.com/file/b19bb382d758d995662d21dc149484c3?bkt=p2-nj-897&fid=422877698-250528-46527744964142&time=1418726215&sign=FDTAXERLB-DCb740ccc5511e5e8fedcff06b081203-kfAjPZ3DYzb1sQgqexyHIKABjIc%3D&to=qb&fm=Qin,B,U,ny&newver=1&newfm=1&flow_ver=3&sl=81723464&expires=1418728119&rt=sh&r=448629972&mlogid=1246248485&sh=1&vuk=-&vbdid=844524738&fin=command_line_tools_for_osx_10_10_june_2014.dmg
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
