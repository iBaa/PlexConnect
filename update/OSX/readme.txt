How to install OpenConnect (if updating OpenConnect you must perform steps 1 & 2 again to get the updated scripts prior to launching the new app)

Step 1

-- kill plexconnect if its running or unload your plist if used to autostart PlexConnect
In your PlexConnect directory make these new folders /update/OSX <-----case sensitive (OSX is a subfolder of update)
Copy all the files from here to the new OSX folder you just created
(If you have a plist that autostarts PlexConnect you can ignore killing PlexConnect, OpenConnect will do this for you)

Step 2 enter these commands into terminal:

sudo su 
## Naviagate to your PlexConnect base directory
mkdir -p /update/OSX
## Naviagate to the new /update/OSX folder <-----OSX is a subfolder of Update.
./install.bash

step 3

-- To install OpenConnect app on osx simply run this app (OpenConnect has built-in in PlexConnect updater function):

-- https://www.dropbox.com/sh/t45w85ktydh0dvu/6-8W2POoM4

A few notes about OpenConnect:

OpenConnect requires a plist for the update function to work just use the expert or guide mode to install PlexConnect autostarting plists. If you have a existing plist OpenConnect can easily swap back and forth from the bash or non-bash plist by simply choosing which one you desire from the install PlexConnect function. If one of the plists do not work for you choose the other and test functionality. The best way to test is by installing a plist then restarting your OSX system and logging in. Finally see if your appletv is displaying PlexConnect if it is your plist has been properly installed. This app is designed to automatically keep PlexConnect up to date for you so if there is anything you want to backup please do so prior to using this app. There is two options bash or non-bash, use which ever one works for you and starts at boot. The bash plist is the standard plist to autostart PlexConnect on OSX. The non-bash is for compadibility and may work for older OSX versions.
