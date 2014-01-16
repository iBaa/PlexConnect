#!/bin/bash

## check for git and install if needed
git

## define update.bash as executable
chmod +x update.bash

## copy update bash so it can be ran without permissions
cp update.bash /usr/bin

## cd to PlexConnect directory
cd "$( cd "$( dirname "$0" )" && pwd )"/../..

## change permissions of .git so update.bash can be ran without su
chown -R $USER .git

## warn user to install git prior to updates
echo IF YOU CANCELED THE INSTALLATION OF GIT RERUN THIS SCIPT. DO NOT CONTINUE UNTIL GIT IS INSTALLED YOU HAVE BEEN WARNED!
echo PROCEED ONLY IF YOU INSTALLED GIT PRIOR
