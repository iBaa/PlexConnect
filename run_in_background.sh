sudo rm -f PlexConnect.log 
nohup sudo python PlexConnect.py &
disown %1
