"Plex @ aTV - think different..."

What is it good for?
We all want the pleasure of Plex on the big screen - in this case driven by an AppleTV.
Unfortunately there are officially no Apps allowed, most of the time a jailbreak is late (iOS 5.2?) or not avaiable at all (aTV3?).

This is a collection of files developed for the little project described in:
http://forums.plexapp.com/index.php/topic/57831-plex-atv-think-different

See also https://github.com/finkdiff/ATVBrowser-script/tree/atvxml for a project with similar purpose, all javascript.


How does it work?
The basic idea is, to...
- re-use an already available app (like youtube, vimeo, apple trailers, ...)
- re-route the request to your local Plex Media Server
- re-work the reply to fit into aTV's communication scheme
- let iOS do the rest


How can I use it?
Just a view steps...
- store DNSServer.py and WebServer.py in a local directory
- in both files, adapt the IP addresses to your local setup
- sudo both scripts
- point aTV's DNS setting to the computer running the scripts
- run the trailer App and check out both script's terminal output


Any more detailed information?
DNSServer.py
This is a small DNS server (hence the name) that is now called whenever aTV needs to resolve an internet address. To hijack the trailer App, we will intercept and re-route all queries to trailers.apple.com. Every other query will be forwarded to the next, your original DNS.
WebServer.py
This script provides the directory content of "assets" to aTV. Additionally it will forward ATV's directory requests to PMS and provide a aTV compatible XML back.
Serving media does not work currently. You can try... but it will most likely crash your aTV, going through a fresh reboot and leave you on the main page.


Disclaimer:
The software is provided as is. It might work as expected - or not. Just don't blame me.
