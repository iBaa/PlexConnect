cd /Applications

if [ -s OpenPlex.app ]
then
rm -R OpenPlex.app
fi

if [ -s updater.app ]
then
rm -R updater.app
fi

cd /Applications/OpenPlex/updater

if [ -s updater.app ]
then
rm -R updater.app
fi

cd /Applications/OpenPlex/10.6

if [ -s OpenPlex.app ]
then
rm -R OpenPlex.app
fi

cd /Applications/OpenPlex/10.7

if [ -s OpenPlex.app ]
then
rm -R OpenPlex.app
fi

