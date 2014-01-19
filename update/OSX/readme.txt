How to install OpenConnect.

Step 1

-- kill plexconnect if its running or unload your plist if used to autostart PlexConnect
In your PlexConnect directory make two new folders /update/OSX <-----case sensitive
Copy all the files from here to the new OSX folder you just created
(If you have a plist that autostarts PlexConnect you can ignore killing PlexConnect, OpenConnect will do this for you)

Step 2 enter these commands into terminal:

sudo su 
## Naviagate to the new /update/OSX folder <-----OSX is a subfolder of Update.
./install.bash

step 3

-- To install OpenConnect app on osx simply run this app (OpenConnect has built-in in PlexConnect updater function):

-- http://stashbox.org/1370231/OpenConnect.zip
