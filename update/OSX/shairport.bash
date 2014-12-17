# Check for brew and install it
if [ ! -f "/usr/local/bin/brew" ]; then
  ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
  brew prune
fi

brew tap homebrew/headonly
brew install shairport --HEAD --with-libao

sudo xcodebuild -license

bindir="/usr/local/bin"
if [ -d "$bindir" ]; then
echo 'bin dir found'
else
sudo mkdir -p /usr/local/bin
fi

shairportdir="/Applications/shairport"
if [ -d "$shairportdir" ]; then
rm -rf /Applications/shairport
fi
cd /Applications
export PATH=/usr/local/git/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH
git clone https://github.com/abrasive/shairport.git
cd /Applications/shairport
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
