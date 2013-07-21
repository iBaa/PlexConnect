sudo rm -f out.log
nohup sudo python PlexConnect.py > out.log &
disown %1
