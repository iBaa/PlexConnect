#!/bin/sh
OSX_VERS=$(sw_vers -productVersion | awk -F "." '{print $2}')
 
if [ "$OSX_VERS" -eq 6 ]; then
cd /Applications
curl -L https://github.com/wahlmanj/OpenPlex/raw/master/10.7/OpenPlex.zip > OpenPlex.zip
ditto -xk OpenPlex.zip /Applications
rm OpenPlex.zip
open OpenPlex.app
echo $OSX_VERS
elif [ "$OSX_VERS" -eq 7 ]; then
cd /Applications
curl -L https://github.com/wahlmanj/OpenPlex/raw/master/10.7/OpenPlex.zip > OpenPlex.zip
ditto -xk OpenPlex.zip /Applications
rm OpenPlex.zip
open OpenPlex.app
echo $OSX_VERS
elif [ "$OSX_VERS" -eq 8 ]; then
cd /Applications
curl -L https://github.com/wahlmanj/OpenPlex/raw/master/10.6/OpenPlex.zip > OpenPlex.zip
ditto -xk OpenPlex.zip /Applications
rm OpenPlex.zip
open OpenPlex.app
echo $OSX_VERS
elif [ "$OSX_VERS" -eq 9 ]; then
cd /Applications
curl -L https://github.com/wahlmanj/OpenPlex/raw/master/10.6/OpenPlex.zip > OpenPlex.zip
ditto -xk OpenPlex.zip /Applications
rm OpenPlex.zip
open OpenPlex.app
echo $OSX_VERS
elif [ "$OSX_VERS" -eq 10 ]; then
cd /Applications
curl -L https://github.com/wahlmanj/OpenPlex/raw/master/10.6/OpenPlex.zip > OpenPlex.zip
ditto -xk OpenPlex.zip /Applications
rm OpenPlex.zip
open OpenPlex.app
echo $OSX_VERS
fi
