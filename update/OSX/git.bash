export PATH=$PATH:/usr/local/git/bin:/usr/bin:/opt/local/bin:/usr/local/bin/git:/usr/local/bin
cd /Applications
portsdir="/Applications/MacPorts-2.3.1"
if [ -d "$portsdir" ]; then
echo 'bin dir found'
else
curl -O https://distfiles.macports.org/MacPorts/MacPorts-2.3.1.tar.bz2 
tar xf MacPorts-2.3.1.tar.bz2; cd /Applications/MacPorts-2.3.1
./configure && make && sudo make install
port -v selfupdate
port install git
fi

