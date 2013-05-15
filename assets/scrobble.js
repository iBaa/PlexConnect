function scrobbleMenu(type, ratingKey, addrPMS) {
  var xmlstr = '<?xml version="1.0" encoding="UTF-8"?><atv><head><script src="http://trailers.apple.com/scrobble.js"/></head> \
                <body><optionList id="scrobble.optionDialog"> \
                <title>$$title$$</title><items><oneLineMenuItem id="item1" onSelect="scrobble($$addrPMS1$$, $$ratingKey1$$);atv.unloadPage();"> \
                <label>             Mark as Watched</label></oneLineMenuItem> \
                <oneLineMenuItem id="item1" onSelect="unscrobble($$addrPMS2$$, $$ratingKey2$$);atv.unloadPage();"> \
                <label>           Mark as UnWatched</label></oneLineMenuItem> \
                </items></optionList></body></atv>';
  
  if (type=="Episode") xmlstr = xmlstr.replace("$$title$$", "Episode");
  if (type=="Season") xmlstr = xmlstr.replace("$$title$$", "Entire Season");
  if (type=="Show") xmlstr = xmlstr.replace("$$title$$", "Entire Show");
  
  xmlstr = xmlstr.replace("$$ratingKey1$$", "'" + ratingKey + "'");
  xmlstr = xmlstr.replace("$$ratingKey2$$", "'" + ratingKey + "'");
  xmlstr = xmlstr.replace("$$addrPMS1$$", "'" + addrPMS + "'");
  xmlstr = xmlstr.replace("$$addrPMS2$$", "'" + addrPMS + "'");

 	var doc = atv.parseXML(xmlstr);
  
  atv.loadXML(doc);
};

function loadPage(url)
{
	var req = new XMLHttpRequest();
	req.open('GET', url, true);
	req.send();
};

function scrobble(addrPMS, ratingKey) {
  loadPage("http://" + addrPMS + "/:/scrobble?key=" + ratingKey + "&identifier=com.plexapp.plugins.library"); 
};

function unscrobble(addrPMS, ratingKey) {
  loadPage("http://" + addrPMS + "/:/unscrobble?key=" + ratingKey + "&identifier=com.plexapp.plugins.library"); 
};
