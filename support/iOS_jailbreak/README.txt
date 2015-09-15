PlexConnect on iOS (jailbroken)

Install PlexConnect on your iOS Device (not for aTV see aTV_Jailbreak in support folder for aTV instructions)
- SSH into iOS device (default user is root and default password is alpine)
- Paste this into the ssh session:

apt-get -y install git; rm -R /Applications/PlexConnect; cd /Applications; git clone git://github.com/ibaa/PlexConnect.git; cd /Applications/PlexConnect/support/iOS_jailbreak; chmod +x installios.bash; ./installios.bash

Done!

This will start PlexConnect on your iOS device @ boot via wifi. If you change your IP address or wifi network you will need to reboot your iOS device or ssh back into the iOS device and restart the launch daemon. You can easily do this by entering your iOS device via ssh and typing this:

restart.bash

A good way to keep PlexConnect active is to turn on airplane mode then turn your wifi back on while airplane mode is active otherwise you iOS device will put your wifi to sleep because it doesn’t realize PlexConnect is running in the background.

