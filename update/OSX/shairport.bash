sudo xcodebuild -license
sudo port install git libao pkgconfig p5-io-socket-inet6 p5-libwww-perl p5-crypt-openssl-rsa
cd /Applications
git clone https://github.com/abrasive/shairport.git
cd /Applications/shairport
make
cp shairport /usr/local/bin
sudo dscl . -create /Groups/_shairport RealName "AirPlay Daemon Group"
sudo dscl . -create /Groups/_shairport PrimaryGroupID 235
sudo dscl . -create /Users/_shairport RealName "AirPlay Daemon"
sudo dscl . -create /Users/_shairport UniqueID 235
sudo dscl . -create /Users/_shairport PrimaryGroupID 235
sudo dscl . -create /Users/_shairport UserShell /usr/bin/false
sudo dscl . -create /Users/_shairport NFSHomeDirectory /var/empty
cd /Applications/shairport/scripts/osx
sudo cp org.mafipulation.shairport.plist /Library/LaunchDaemons
cd /Library/LaunchDaemons
sudo chown root:wheel org.mafipulation.shairport.plist
sudo chmod 644 org.mafipulation.shairport.plist
sudo launchctl load org.mafipulation.shairport.plist
