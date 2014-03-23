#!/bin/bash

START_HERE="/applications/plexconnect";

cd $START_HERE;

for d in $(find . -maxdepth 1 -mindepth 1 -type d); do
        echo -e "$d";
        cd $d;
        git remote -v;
        git pull;
        cd $START_HERE;
done
