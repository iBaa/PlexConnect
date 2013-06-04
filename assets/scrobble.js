/*
 * Build Watched/Unwatched menu
 */
function scrobbleMenu(type, ratingKey, addrPMS) {
  var xmlstr = '<?xml version="1.0" encoding="UTF-8"?><atv><head><script src="http://trailers.apple.com/scrobble.js"/></head> \
                <body><optionList id="scrobble.optionDialog"><title>' + type + '</title><items> \
								<oneLineMenuItem id="item1" onSelect="scrobble(\'' + addrPMS + '\', \'' + ratingKey + '\');atv.unloadPage();"> \
								<label>             Mark as Watched</label></oneLineMenuItem> \
                <oneLineMenuItem id="item1" onSelect="unscrobble(\'' + addrPMS + '\', \'' + ratingKey + '\');atv.unloadPage();"> \
                <label>           Mark as Unwatched</label></oneLineMenuItem> \
                </items></optionList></body></atv>';
 	var doc = atv.parseXML(xmlstr);
  atv.loadXML(doc);
};

/*
 * scrobble or unscrobble a ratingKey
 */
function scrobble(addrPMS, ratingKey) {
	var url = "http://" + addrPMS + "/:/scrobble?key=" + ratingKey + "&identifier=com.plexapp.plugins.library";
	var req = new XMLHttpRequest();
	req.open('GET', url, true);
	req.send();
};

function unscrobble(addrPMS, ratingKey) {
	var url = "http://" + addrPMS + "/:/unscrobble?key=" + ratingKey + "&identifier=com.plexapp.plugins.library";
	var req = new XMLHttpRequest();
	req.open('GET', url, true);
	req.send();
};
