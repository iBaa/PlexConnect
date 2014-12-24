#!/bin/bash

cd ~/.Trash/

osascript -e 'tell app "Finder" to empty'
echo 'Trash emptied if no corrupt files present in trash can'
