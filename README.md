# Plex Connect
or: "Plex @ aTV - think different..."

We all want the pleasure of Plex on the big screen - in this case driven by an AppleTV.
Unfortunately there are officially no Apps allowed on AppleTV, most of the time a jailbreak is late (iOS 5.2?) or not avaiable at all (aTV3?).

This is a collection of files developed for the little project described in [Plex Forum][].
See also [ATVBrowser][] for a project with similar purpose, all javascript.


## How does it work?
The basic idea is, to...
- re-use an already available app (like YouTube, Vimeo, Apple Trailers, ...)
- re-route the request to your local Plex Media Server
- re-work the reply to fit into AppleTV's XML communication scheme
- let iOS do the rest


## Installation
  ```sh
  # Installation
  git clone https://github.com/iBaa/PlexConnect.git
  # Updating
  cd PlexConnect
  git pull
  ```
  > If you don't have Git, you can download [ZIP][] file and extract files to a local directory.


## Usage
- in ```Settings.py```, adapt the IP addresses to your local setup
- ```sudo ./PlexConnet.py```
- set your AppleTV's DNS address to the computer running PlexConnect
- run the Trailer App and check the terminal output


## More detailed Information about the files
* __PlexConnect.py__ - 
Main script file, invoking the DNSServer and WebServer into seperate processes.
* __PlexGDM.py__ - 
Auto discovery of running Plex Media Servers: Good Day Mate!
* __DNSServer.py__ - 
This is a small DNS server (hence the name) that is now called whenever aTV needs to resolve an internet address. To hijack the trailer App, we will intercept and re-route all queries to trailers.apple.com. Every other query will be forwarded to the next, your original DNS.
* __WebServer.py__ - 
This script provides the directory content of "assets" to aTV. Additionally it will forward aTV's directory requests to PMS and provide a aTV compatible XML back.
Every media (video, thumbnails...) is URL-wise connected to PMS, so aTV directly accesses the Plex database.
* __XMLConverter.py__
This script contains the XML adaption from Plex Media Server's response to valid aTV XML files.
* __Settings.py__ - 
Basic settings collection. This should be the only file to modify.


## Disclaimer
The software is provided as is. It might work as expected - or not. Just don't blame me.


[ATVBrowser]: https://github.com/finkdiff/ATVBrowser-script/tree/atvxml
[Plex Forum]: http://forums.plexapp.com/index.php/topic/57831-plex-atv-think-different
[ZIP]: https://github.com/iBaa/PlexConnect/archive/XML_templates.zip