if [ -s /Applications/OpenPlex/10.6/OpenPlex.app ]
then
rm -Rf /Applications/OpenPlex/10.6/OpenPlex.app
fi

if [ -s /Applications/OpenPlex/10.7/OpenPlex.app ]
then
rm -Rf /Applications/OpenPlex/10.7/OpenPlex.app
fi

if [ -s /Applications/OpenPlex/updater/updater.app ]
then
rm -Rf /Applications/OpenPlex/updater/updater.app
fi

cd /Applications/OpenPlex 
export PATH=/usr/local/git/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH
git remote update
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse @{u})
BASE=$(git merge-base @ @{u})
if [ $LOCAL = $REMOTE ]; then
echo "No app updates avaliable" 							
elif [ $LOCAL = $BASE ]; then
echo "OpenPlex update available, Installing..."
updatewcbash.bash
cd /Applications/OpenPlex/updater
ditto -xk updater.zip /Applications/OpenPlex/updater
cd /Applications/OpenPlex/updater
open updater.app
elif [ $REMOTE = $BASE ]; then
echo "Need to push"
else
echo "Diverged"
fi
