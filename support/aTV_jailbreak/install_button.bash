#!/bin/bash

echo 'Installing PlexConnect Button...'

## save path to installer files
cd "$( cd "$( dirname "$0" )" && pwd )"
InstallerPath=${PWD}

## find PlexConnect main path
cd ../..
PlexConnectPath=${PWD}

## /Library/Managed Preferences/mobile/com.apple.frontrow.plist
## -> AddSite hack - see https://intrepidusgroup.com/insight/2013/09/rpi-atv/
src="${InstallerPath}/com.apple.frontrow.plist"
dest="/Library/Managed Preferences/mobile/com.apple.frontrow.plist"
if [ -f "$dest" ]; then
    echo
    echo $dest' already installed.'
    echo 'make sure <key>F2BE6C81-66C8-4763-BDC6-385D39088028</key> is already in...'
    echo 'see '$src' for implementation.' 

else
    ## copy to /Library/Managed Preferences/mobile
    cp "$src" "$dest"

fi

## /User/Library/Application Support/Front Row/ExtraInternetCategories.plist
src="${InstallerPath}/ExtraInternetCategories.plist"
dest="/User/Library/Application Support/Front Row/ExtraInternetCategories.plist"
if [ -f "$dest" ]; then
    echo
    echo $dest' already installed.'
    echo 'make sure PlexConnect with its correct URL is already in...'
    echo 'see '$src' for implementation.' 

else
    ## replace __INSTALLERPATH__ in default ExtraInternetCategories.plist
    ## save directly to /User/Library/Application Support/Front Row
    sed -e "s/__INSTALLERPATH__/${InstallerPath//\//\\/}/" "$src" > "$dest"

fi

## replace __INSTALLERPATH__ in default bag_dflt.plist
## save directly to bag.plist
sed -e "s/__INSTALLERPATH__/${InstallerPath//\//\\/}/" "${InstallerPath}/bag_dflt.plist" > "${InstallerPath}/bag.plist"
