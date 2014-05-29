OpenPlex Tutorial

The first thing you should do if you are are running PlexConnect is stop it if its running via terminal or using a different app. If you are upgrading from OpenConnect you need to backup your certs from /applications/PlexConnect/assets/certificates then delete the plexconnect folder then click the settings icon and then click the Github icon.  

On first run of the app or any updates of the app you must click the Github icon to get the new app dependencies for the app to function properly. This is done by clicking the settings icon on the fist window that opens when you open the app. Once this is complete the app will function without a password at this point unless you need to update the app. Every time you update the app by clicking the Github icon you will need to pick a new theme again from the drop-down menu.

Installer Window:

Once in the installer window (settings icon) You need to Choose a theme. Once the theme has completed installation you need to install the pillow installer for the themes to function properly.

If you need a installation guide it is provided otherwise skip the step.

You can then load your certs by clicking open certs folder button which will open the cert folder so you can copy your old certs to the required cert folder. You can also place you old certs in the /applcations/plexconnect_BACKUP base folder (-NOT- /applications/plexconnect_BACKUP/assets/certificates) and click the load backup certs button to load them for you by just clicking that button. Delete certs will delete your certs from the /applcations/plexconnect/assets/certificates folder so please have a backup if this is your only copy which I recommend you place in the /applications/plexconnect_BACKUP folder for safe keeping. If you have no certs yet you can skip this step.

Once your certs are in place you need to choose the corresponding hijack that meets your old certs. If you have no certs just pick a hijack and certs will be automatically generated for you and your settings.cfg will be set to hijack the corresponding app. You will still need to load your new certs on your apple tv if they are not present and the Installation Guide button will guide you how to do so via the network method which is by far the easiest. 

WebConnect is a optional webgui to manage plexconnect and your mac using any web browser on any device anywhere in the world or just at home. If you want it to work outside your network you will need to open port 1234 on your router and point it at your mac.        

The first window has numerous buttons to choose from once plexconnect is installed using the installer:

Start PlexConnect - Starts PlexConnect if its stopped
Update PlexConnect - Stops then updates then starts PlexConnect
Stop PlexConnect - Stops PlexConnect if its running
Show Log - Show the status of plexconnect (sometimes it needs to be refreshed via the system log app when starting or stoping plexconnect) 
Hide Log - Hides the status log
Quit - Quits OpenPlex
The settings icon open the main installer window
The i button opens the support window

Support:

Forum - takes you to the PlexConnect forums
Wiki — takes you to the PlexConnect wiki
Roadmap - takes you to the current PlexConnect roadmap
