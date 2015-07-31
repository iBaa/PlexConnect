# PlexConnect
or: "Plex @ aTV - think different..."

We all want the pleasure of Plex on the big screen - in this case driven by an AppleTV.
Unfortunately there are officially no Apps allowed on AppleTV, most of the time a jailbreak is late (iOS 5.2?) or not available at all (aTV3).

This is a collection of files developed for the little project described in this [Plex Forum thread][].
See also the discontinued [ATVBrowser][] for a project with similar purpose, all javascript.

For more information, like detailed Installation Guides, FAQs and similar, visit the [Wiki][].


## How does it work?
The basic idea is, to...
- re-use an already available app (like YouTube, Vimeo, ... in this case: Apple Trailers)
- re-route the request to your local Plex Media Server
- re-work the reply to fit into AppleTV's XML communication scheme
- let iOS do the rest


## Requirements
- Python 2.6.x with minor issues: ElementTree doesn't support tag indices.
- Python 2.7.x recommended.


## Installation
```sh
# Installation
git clone https://github.com/iBaa/PlexConnect.git
# Updating
cd PlexConnect
git pull
```
> If you don't have Git, you can download [ZIP][] file and extract files to a local directory.

- create HTTPS/SSL certificate
- install certificate to ```assets/certificate/```
- install certificate on aTV

See the [Wiki - Install Guide][] for additional documentation.


## Usage
```sh
# Run with root privileges
sudo ./PlexConnect.py
```
> Depending on your OS, you might only need ```PlexConnect.py```. Or ```python PlexConnect.py``` or ...

- set your AppleTV's DNS address to the computer running PlexConnect
- run the Trailer App

See the [Wiki - Advanced Settings][] for more details on configuration and advanced settings.


## More detailed Information about the files
* __PlexConnect.py__ - 
Main script file, invoking the DNSServer and WebServer into seperate processes.
* __PlexAPI.py__ - 
Collection of Plex Media Server/MyPlex "connector functions": Auto discovery of running PMSs: Good Day Mate! // XML interface to local PMSs // MyPlex integration
* __DNSServer.py__ - 
This is a small DNS server (hence the name) that is now called whenever aTV needs to resolve an internet address. To hijack the trailer App, we will intercept and re-route all queries to trailers.apple.com. Every other query will be forwarded to the next, your original DNS.
* __WebServer.py__ - 
This script provides the directory content of "assets" to aTV. Additionally it will forward aTV's directory requests to PMS and provide a aTV compatible XML back.
Every media (video, thumbnails...) is URL-wise connected to PMS, so aTV directly accesses the Plex database.
* __XMLConverter.py__ - 
This script contains the XML adaption from Plex Media Server's response to valid aTV XML files.
* __Settings.py__ - 
Basic settings collection. Creates ```Settings.cfg``` at first run - which may be modified externally.
* __ATVSettings.py__ - 
Handles the aTV settings like ViewModes or Transcoder options. Stores aTV settings in ```ATVSettings.cfg```.
* __Localize.py__ -
Holds a couple of utility functions for text translation purposes. Uses dictionaries from ```assets/locales/```.
* __Subtitle.py__ -
Subtitle parser functions for PlexConnect's own renderer, converts subs to JSON for easy transfer to aTV.
* __PILBackgrounds.py__ -
Modify and cache fanart images for use by aTV.


## License and Disclaimer
This software is open-sourced under the MIT Licence (see ```license.txt``` for the full license).
So within some limits, you can do with the code whatever you want. However, if you like and/or want to re-use it, we really appreciate a [Donation][].

The software is provided as is. It might work as expected - or not. Just don't blame us.


[ATVBrowser]: https://github.com/finkdiff/ATVBrowser-script/tree/atvxml
[Plex Forum thread]: http://forums.plex.tv/discussion/57831/plex-atv-think-different/p1
[ZIP]: https://github.com/iBaa/PlexConnect/archive/master.zip
[Wiki]: https://github.com/iBaa/PlexConnect/wiki
[Wiki - Install Guide]: https://github.com/iBaa/PlexConnect/wiki/Install-Guide
[Wiki - Advanced Settings]: https://github.com/iBaa/PlexConnect/wiki/Settings-for-advanced-use-and-troubleshooting
[Donation]: http://forums.plex.tv/discussion/80675/donations-donations/p1
