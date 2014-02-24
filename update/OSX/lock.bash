#!/bin/bash

if [[ -z $1 ]]; then
/System/Library/CoreServices/Menu\ Extras/User.menu/Contents/Resources/CGSession -suspend
else
 USERID=`id -u $1`;
  if [[ -z $USERID ]]; then
    exit -1;
  fi;
  /System/Library/CoreServices/Menu\ Extras/User.menu/Contents/Resources/CGSession -switchToUserID $USERID
fi;
