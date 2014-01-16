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
