#!/bin/bash
dpkg -i python_2.7.6-3_iphoneos-arm.deb
rm python_2.7.6-3_iphoneos-arm.deb
cp Settings_atv3.cfg /Applications/PlexConnect/Settings.cfg
cp iMovie.* /Applications/PlexConnect/assets/certificates/
cp /Applications/PlexConnect/assets/icons/icon\@720.png /private/var/mobile/Library/Caches/AppleTV/MainMenu/iMovieNewAuth\@720.png
cp /Applications/PlexConnect/assets/icons/icon\@1080.png /private/var/mobile/Library/Caches/AppleTV/MainMenu/iMovieNewAuth\@1080.png
echo '## PlexConnect managed app' >> /etc/hosts
echo '127.0.0.1 www.icloud.com' >> /etc/hosts
echo '## Avoid firmware update' >> /etc/hosts
echo '127.0.0.1 mesu.apple.com' >> /etc/hosts
echo '127.0.0.1 appldnld.apple.com' >> /etc/hosts
echo '127.0.0.1 appldnld.apple.com.edgesuite.net' >> /etc/hosts
./install_atv3.bash