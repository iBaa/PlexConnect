/*
 * Build Watched/Unwatched menu
 */
function scrobbleMenu(type, ratingKey, addrPMS) {
  var xmlstr = '<?xml version="1.0" encoding="UTF-8"?><atv><head><script src="http://aTV.PlexConnect/js/scrobble.js"/></head> \
                <body><optionList id="scrobble.optionDialog"><title>' + type + '</title><items> \
								<oneLineMenuItem id="item1" onSelect="scrobble(\'' + addrPMS + '\', \'' + ratingKey + '\');atv.unloadPage();"> \
								<label>             Mark as Watched</label></oneLineMenuItem> \
                <oneLineMenuItem id="item2" onSelect="unscrobble(\'' + addrPMS + '\', \'' + ratingKey + '\');atv.unloadPage();"> \
                <label>           Mark as Unwatched</label></oneLineMenuItem> \
								<oneLineMenuItem id="item3" onSelect="selectArtwork(\'' + addrPMS + '\', \'' + ratingKey + '\');"> \
                <label>              Change Artwork</label></oneLineMenuItem> \
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
	req.open('GET', url, false);
	req.send();
};

function unscrobble(addrPMS, ratingKey) {
	var url = "http://" + addrPMS + "/:/unscrobble?key=" + ratingKey + "&identifier=com.plexapp.plugins.library";
	var req = new XMLHttpRequest();
	req.open('GET', url, false);
	req.send();
};


/*
 * Select Artwork
 */
function selectArtwork(addrPMS, ratingKey) {
	// Load PMS metadata xml
	var url = "http://" + addrPMS + "/library/metadata/" + ratingKey + "/posters";
	var req = new XMLHttpRequest();
  req.onreadystatechange = function()
  {
    try
    {
      if(req.readyState == 4)
      {
        doc = req.responseXML;
      }
    }
		catch(e)
    {
        req.abort();
		}
	}
  req.open('GET', url, false);
  req.send();

	// Build xml menu
	var posters = doc.evaluateXPath("descendant::Photo");
	var colCount = "5";
	if (posters.length <= 5) colCount = posters.length.toString();
	
	var xml = '<?xml version="1.0" encoding="UTF-8"?><atv><head><script src="http://aTV.PlexConnect/js/scrobble.js"/></head> \
						<body><scroller id="poster_selector"><header><simpleHeader><title>Select Artwork</title></simpleHeader></header> \
						<items><collectionDivider alignment="left"><title></title></collectionDivider><shelf id="coverflow" columnCount="' + colCount +'"> \
						<sections><shelfSection><items>';

	for(var i = 0; i < posters.length; ++i)
	{
		var poster = posters[i];
		var posterThumb = poster.getAttribute('thumb');
		var posterURL = poster.getAttribute('key');
		var selected = poster.getAttribute('selected');
		var title = '';
		if (selected == '1') title = 'Current Artwork';
		xml = xml + '<goldenPoster id="poster" alwaysShowTitles="true" onSelect="loadNewArtwork(\'' + addrPMS + '\', \'' + ratingKey + '\', \'' + posterURL + '\');atv.unloadPage();">';
		xml = xml + '<title>' + title + '</title><image>http://' + addrPMS + posterThumb + '</image>';
		xml = xml + '<defaultImage>resource://Poster.png</defaultImage></goldenPoster>';
	};
	xml = xml + '</items></shelfSection></sections></shelf><collectionDivider alignment="left"><title></title> \
							 </collectionDivider></items></scroller></body></atv>';
	
	var menuDoc = atv.parseXML(xml);
	atv.loadXML(menuDoc);
};

/*
 * Update Plex library with new artwork
 */
function loadNewArtwork(addrPMS, ratingKey, posterURL)
{
	if (posterURL.indexOf('library') !== -1)
	{
		var urlParts = posterURL.split('=');
		posterURL = urlParts[1];
	}
	var url = "http://" + addrPMS + "/library/metadata/" + ratingKey + "/poster?url=" + posterURL;
	var req = new XMLHttpRequest();
	req.open('PUT', url, false);
	req.send();
};