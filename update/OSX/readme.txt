How to automatically update PlexConnect.

Step 1

-- kill plexconnect if it running or unload your plist if used to autostart PlexConnect
In your PlexConnect directory make two new folders /update/OSX <-----case sensitive
Copy the install.bash and update.bash from here to the new OSX folder you just created

Step 2 enter these commands into terminal:

sudo su 
## Naviagate to the /update/OSX folder
./install.bash

step 3

-- To update on osx simply type this into terminal:

sudo su
update.bash

## OR

-- download this automator generated app http://stashbox.org/1367321/updater.zip
