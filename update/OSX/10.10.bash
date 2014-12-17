#!/bin/bash
export PATH=/usr/local/git/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH
cd /Applications
rm -R OpenPlex.app
git clone https://github.com/wahlmanj/OpenPlex.git
cd /Applications/OpenPlex/10.10
ditto -xk OpenPlex.zip /Applications/OpenPlex/10.10
cp -R OpenPlex.app /Applications
rm -R /Applications/OpenPlex
