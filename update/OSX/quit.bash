killall OpenPlex
sleep 2
open -a /Applications/OpenPlex.app
osascript -e 'display notification "OpenPlex updated..." with title "OpenPlex Status"'
