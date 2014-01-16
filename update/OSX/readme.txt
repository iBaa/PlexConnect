How to automatically update PlexConnect.

Step 1

-- kill plexconnect if it running or unload you plist if used to autostart
In your PlexConnect directory make two new folders /update/OSX <-----case sensitive
Copy the install.bash and update.bash from here to the new OSX folder you just created

Step 2 enter these commands into terminal:

sudo su 
## Naviagate to the /update/OSX folder
chmod +x install.bash
./install.bash

step 3

-- To update on osx simply type update.bash from terminal (no need to login)

or

-- download this automator generated app http://stashbox.org/1365560/updater.zip



Optional:

If you want to have this app automatically update during every boot of your system just add the updater app to your login
items.
