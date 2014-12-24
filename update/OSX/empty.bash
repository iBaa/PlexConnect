#!/bin/bash -c 'echo This file is meant to be sourced.'

alias rm='del'
  # make rm(1) safe.
  # Remove or comment-out this line to return to normal rm(1) functionality.

function del ()
{
  if declare -F trash >/dev/null
  then
    trash "$@"
  else
    command rm -i "$@"
  fi
}

function trash ()
{
  local F
  local HOME_DEVICE="$(stat -f %Sd "$HOME")"
  local TRASHCAN=~/.Trash
    # Set this in advance _outside_ the loop below
  for F in "$@"
  do
    if ! test -e "$F"
    then
      echo "No such file or directory: $F" 1>&2
      return 4
    fi
    
    local DEVICE="$(stat -f %Sd "$F")"
    
    if [ x"$DEVICE" == x"" ] || [ x"$DEVICE" == x"???" ]
    then
      echo "Can't locate trash for ${F}." 1>&2
      return 3
    fi
    
    if [ x"$DEVICE" != x"$HOME_DEVICE" ]
    then
      TRASHCAN="$(trashOnDevice "$DEVICE")"
    fi
    
    if [ ! -d "${TRASHCAN}" ]
    then
      command rm -f "${TRASHCAN}"
      if ! mkdir -m 700 "${TRASHCAN}"
      then
        echo "$TRASHCAN is inaccessible at this time." | sed 's;'"$HOME"';~;g' 1>&2
        return 1
      fi
    fi
    
    local FinT="$(basename "$F")"
    
    if [ -e "${TRASHCAN}/${FinT}" ]
    then
      FinT="$(date) ${FinT}"
    fi
    
    if ! mv -vn "$F" "${TRASHCAN}/${FinT}"
    then
      echo "Unable to move $F to the trash." 1>&2
      return 2
    fi
  done
  
  local TRASHSIZE="$(du -hs "${TRASHCAN}" 2>/dev/null | cut -f 1)"
  local TRASHCANloc="$(dirname "$TRASHCAN" | sed 's;^/Volumes/\(.*\)/.Trashes;\1;g' | sed 's;'"$HOME"';~;g' | sed 's;^/.Trashes;/;g')"
  echo "${TRASHSIZE:-  0B} in trash on $TRASHCANloc."
}

function emptytrash ()
{
  local TMPIFS="$IFS"
  IFS='
'
  local MOUNTS=( $(mount | sed -n 's:/dev/.* on \(.*\) (.*):\1:p') )
  local TRASHCANs=( "${HOME}/.Trash" $(IFS="$TMPIFS";for i in `seq 0 $(( ${#MOUNTS[@]} - 1 ))`; do echo "${MOUNTS[$i]}/.Trashes/$(id -u)"; done) )
  IFS="$TMPIFS"
  unset TMPIFS

  local TRASH_SIZE
  TRASH_SIZE="$( (for i in "${TRASHCANs[@]}"; do ls "$i"/; done) 2>/dev/null | wc -w)"
  if [ "$TRASH_SIZE" -gt 0 ]
  then 
    echo -n "Emptying trash"
    for i in "${TRASHCANs[@]}"
    do 
      tput smcup
      pushd "$i" 2>/dev/null && {
        srm -frsvz . 2>/dev/null ; popd ;
      }
      tput rmcup
      echo -n .
    done
    local DONE=
    [ `ls "${HOME}/.Trash" | wc -w` == 0 ] && DONE="Done."
    echo "$DONE"
  else 
    echo "Trash is empty."
  fi
}

function trashOnDevice ()
{
  local DEVICE="$1"
  local MOUNT="$(mount | sed -n 's:/dev/'"$DEVICE"' on \(.*\) (.*):\1:p')"
  
  if [ x"$MOUNT" == x"" ] || [ x"$MOUNT" == x"???" ]
  then
    # If no mount point is found, then don't return the path to root!
    return 1
  elif [ x"$MOUNT" == x"/" ]
  then
    # Encourage the resulting path to _not_ start with two slashes
    MOUNT=""
  fi
  
  echo "$MOUNT/.Trashes/$UID"
}

# Usage : seq n m [i]
# echo all integers between n and m using a skip or increment of i
function seq ()
{
  [ "$1" ] || [ "$2" ] || return 1
  
  local x=$1;
  local y=$2;
  local i=${3:-1};
  local seperator="${4:- }"
  while [ $x -le $y ]
  do
    echo -n $x"${seperator}";
    x=$(( $x + $i ));
  done
  echo
}
