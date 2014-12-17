
export PATH=/usr/local/git/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH
cd /Applications
curl -O https://distfiles.macports.org/MacPorts/MacPorts-2.3.1.tar.bz2
tar xf MacPorts-2.3.1.tar.bz2
cd /Applications/MacPorts-2.3.1
./configure && make && sudo make install
sudo cp /opt/local/bin/* /usr/bin
sudo port -v selfupdate
sudo xcodebuild -license
sudo port -v install git libao pkgconfig p5-io-socket-inet6 p5-libwww-perl p5-crypt-openssl-rsa
cd /Applications
git clone https://github.com/abrasive/shairport.git
cd /Applications/shairport
bindir="/usr/local/bin"
if [ -d "$bindir" ]; then
echo 'bin dir found'
else
sudo mkdir -p /usr/local/bin
fi
sudo cp /opt/local/bin/* /usr/bin
export PATH=/usr/local/git/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH
make
cd /Applications/shairport
sudo cp shairport /usr/local/bin
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
sudo launchctl unload org.mafipulation.shairport.plist
sudo launchctl load org.mafipulation.shairport.plist
sudo chmod -R 777 /Applications/shairport
sudo chmod -R 777 /Applications/MacPorts-2.3.1.tar.bz2
sudo chmod -R 777 /Applications/MacPorts-2.3.1
sudo rm -R /Applications/shairport
rm /Applications/MacPorts-2.3.1.tar.bz2
rm -R /Applications/MacPorts-2.3.1
