#!/bin/bash
export PATH=$PATH:/usr/local/git/bin:/usr/bin:/opt/local/bin:/usr/local/bin/git
cd /Applications
rm -R OpenPlex.app
git clone https://github.com/wahlmanj/OpenPlex.git
cd /Applications/OpenPlex/10.6
ditto -xk OpenPlex.zip /Applications/OpenPlex/10.6
cp -R OpenPlex.app /Applications
rm -R /Applications/OpenPlex