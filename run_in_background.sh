sudo rm -f PlexConnect.log 
nohup sudo python PlexConnect.py > /dev/null 2>&1 &
disown %1
