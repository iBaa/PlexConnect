# Plex Connect

We all want the pleasure of Plex on the big screen, in this case driven by an Apple TV.
Unfortunately there are no officially apps allowed on Apple TV, most of the time a jailbreak is late (iOS 5.2?) or not avaiable at all (aTV3?).

This is a collection of files developed for the little project described in [Plex Forum][].

See also [ATVBrowser][] script for a project with similar purpose,but just in javascript.


## How does it work?
The basic idea is, to...
- Re-use an already available app on Apple TV (like YouTube, Vimeo, Apple Trailers, etc.).
- Re-route the request to your local Plex Media Server.
- Re-work the reply to fit into aTV's communication scheme.
- Let iOS do the rest


## Installation
  
  ```sh
  # Installation
  git clone https://github.com/iBaa/PlexConnect.git
  
  # Updating
  cd PlexConnect
  git pull
  ```
  > If you don't have Git, you can donwload [ZIP][] file and extract them in a local directory.
  
## Usage

  * Open ```Settings.py``` and set your IP address.
  * Set your Apple TV DNS address to computer, which running the script.
  * ```sudo ./PlexConnect.py```
  * Run the Trailer app in Apple TV and check out terminal output.

## Information about files
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
