#!/bin/bash

## update sources & install dependencies
apt-get -y update
apt-get -y upgrade
apt-get -y install cydia
apt-get -y install wget

## trash PlexConnect Folder if exists to avoid database errors
if [ -s /Applications/PlexConnect ]
then
rm -rf /Applications/PlexConnect
fi

## clone Theme
cd /Applications
git clone git://github.com/iBaa/PlexConnect.git

## create desired Certs
cd /Applications/PlexConnect
echo "Which certs would you like to generate? Press 1 for Trailers or 2 for iMovie"
select yn in "Trailers" "iMovie"; do
case $yn in
Trailers ) openssl req -new -nodes -newkey rsa:2048 -outform pem -out ./assets/certificates/trailers.cer -keyout ./assets/certificates/trailers.key -x509 -days 3650 -subj "/C=US/CN=trailers.apple.com"
cat ./assets/certificates/trailers.cer ./assets/certificates/trailers.key >> ./assets/certificates/trailers.pem; break;;
iMovie ) openssl req -new -nodes -newkey rsa:2048 -outform pem -out ./assets/certificates/trailers.cer -keyout ./assets/certificates/trailers.key -x509 -days 3650 -subj "/C=US/CN=www.icloud.com"
cat ./assets/certificates/trailers.cer ./assets/certificates/trailers.key >> ./assets/certificates/trailers.pem; break;;
esac
done

## use python without env to avoid errors in PlexConect.py
cd /Applications/PlexConnect/support/iOS_jailbreak
cp PlexConnect.py /Applications/PlexConnect
if [ -f /usr/bin/python2.7 ];
then
   echo "Python already installed, skipping"
else
  wget --no-check-certificate https://yangapp.googlecode.com/files/python_2.7.3-3_iphoneos-arm.deb; dpkg -i python_2.7.3-3_iphoneos-arm.deb; rm -R python_2.7.3-3_iphoneos-arm.deb
fi

## install easy systemwide PlexConnect scripts
cp update.bash /usr/bin
cp updatebash.bash /usr/bin
cp restart.bash /usr/bin
cp status.bash /usr/bin

## install autoupdate plist if desired
echo "Do you wish to install this PlexConnect autoupdates? Press 1 for Yes or 2 for No"
select yn in "Yes" "No"; do
    case $yn in
        Yes ) cp com.plex.plexconnect.auto.plist /Library/LaunchDaemons; chown root /Library/LaunchDaemons/com.plex.plexconnect.auto.plist; chmod 644 /Library/LaunchDaemons/com.plex.plexconnect.auto.plist; launchctl load /Library/LaunchDaemons/com.plex.plexconnect.auto.plist; break;;
        No ) break;;
    esac
done

## install launchctl bash plist & change to default PlexConnect.bash to iOS PlexConnect.bash
/Applications/PlexConnect/support/aTV_jailbreak/install.bash
sleep 3
cp /Applications/PlexConnect/support/iOS_jailbreak/com.plex.plexconnect.bash.plist /Library/LaunchDaemons
launchctl unload /Library/LaunchDaemons/com.plex.plexconnect.bash.plist
launchctl load /Library/LaunchDaemons/com.plex.plexconnect.bash.plist

## Switch hijack if required (sleep 2 to ensure Settings.cfg has been generated)
cd /Applications/PlexConnect
echo "Which app would you like to hijack? Press 1 for Trailers or 2 for iMovie"
select yn in "Trailers" "iMovie"; do
case $yn in
Trailers ) sleep 2; sed -i 's/www.icloud.com/trailers.apple.com/g' Settings.cfg; break;;
iMovie ) sleep 2; sed -i 's/trailers.apple.com/www.icloud.com/g' Settings.cfg; break;;
esac
done
restart.bash
echo "Installation complete. Point your aTV DNS to your iOS Device and upload your cert from your iOS device to complete the process"
