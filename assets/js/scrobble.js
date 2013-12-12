/*
 * Build Watched/Unwatched menu
 */
function scrobbleMenu(PMS_baseURL, accessToken, ratingKey, title, parentURL) {
	var xmlstr = 
'<?xml version="1.0" encoding="UTF-8"?> \
<atv> \
  <head> \
    <script src="{{URL(/js/scrobble.js)}}"/> \
    <script src="{{URL(/js/utils.js)}}"/> \
  </head> \
  <body> \
    <optionList id="scrobble.optionDialog"> \
      <title>' + title + '</title> \
      <items>';

	if (typeof parentURL != 'undefined')
	{
		xmlstr += '\
        <oneLineMenuItem id="item1" onSelect="atv.loadAndSwapURL(\'' + parentURL + '\', \'' + accessToken + '\');"> \
          <label>{{TEXT(View Show)}}</label> \
        </oneLineMenuItem>';
	}
	
	xmlstr += '\
        <oneLineMenuItem id="item2" onSelect="scrobble(\'' + PMS_baseURL + '\', \'' + accessToken + '\', \'' + ratingKey + '\');atv.unloadPage();"> \
          <label>{{TEXT(Mark as Watched)}}</label> \
        </oneLineMenuItem> \
        <oneLineMenuItem id="item3" onSelect="unscrobble(\'' + PMS_baseURL + '\', \'' + accessToken + '\', \'' + ratingKey + '\');atv.unloadPage();"> \
          <label>{{TEXT(Mark as Unwatched)}}</label> \
        </oneLineMenuItem> \
        <oneLineMenuItem id="item4" onSelect="selectArtwork(\'' + PMS_baseURL + '\', \'' + accessToken + '\', \'' + ratingKey + '\');"> \
          <label>{{TEXT(Change Artwork)}}</label> \
        </oneLineMenuItem> \
      </items> \
    </optionList> \
  </body> \
</atv>';
// bug? selectArtwork does not atv.unloadPage()
	var doc = atv.parseXML(xmlstr);
	atv.loadXML(doc);
};

/*
 * scrobble or unscrobble a ratingKey
 */
function scrobble(PMS_baseURL, accessToken, ratingKey)
{
    var url = PMS_baseURL + "/:/scrobble?key=" + ratingKey + "&identifier=com.plexapp.plugins.library";
    if (accessToken!='')
        url = url + '&X-Plex-Token=' + accessToken;
    
	var req = new XMLHttpRequest();
	req.open('GET', url, false);
	req.send();
};

function unscrobble(PMS_baseURL, accessToken, ratingKey)
{
    var url = PMS_baseURL + "/:/unscrobble?key=" + ratingKey + "&identifier=com.plexapp.plugins.library";
    if (accessToken!='')
        url = url + '&X-Plex-Token=' + accessToken;
    
	var req = new XMLHttpRequest();
	req.open('GET', url, false);
	req.send();
};

/*
 * Display the Season List page for the selected Episode or Season's Show
 */
function viewShow(parentURL, accessToken)
{
    atv.loadURL(parentURL);
}

/*
 * Select Artwork
 */
function selectArtwork(PMS_baseURL, accessToken, ratingKey)
{
	// Load PMS metadata xml
  var url = PMS_baseURL + "/library/metadata/" + ratingKey + "/posters";
    if (accessToken!='')
        url = url + '?X-Plex-Token=' + accessToken;
    
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
	var xml = 
'<?xml version="1.0" encoding="UTF-8"?> \
<atv> \
  <head> \
    <script src="{{URL(/js/scrobble.js)}}"/> \
  </head> \
  <body> \
    <scroller id="poster_selector"> \
      <header> \
        <simpleHeader> \
          <title>{{TEXT(Select Artwork)}}</title> \
        </simpleHeader> \
      </header> \
      <items> \
        <collectionDivider alignment="left"> \
          <title></title> \
        </collectionDivider> \
        <shelf id="coverflow" columnCount="' + colCount +'"> \
          <sections> \
            <shelfSection> \
              <items>';

	for(var i = 0; i < posters.length; ++i)
	{
		var poster = posters[i];
		var posterThumb = poster.getAttribute('thumb');
		var posterURL = poster.getAttribute('key');
		var selected = poster.getAttribute('selected');
		var title = '';
		if (selected == '1') title = "{{TEXT(Current Artwork)}}";

    xml = xml + ' \
                <goldenPoster id="poster" alwaysShowTitles="true" onSelect="loadNewArtwork(\'' + PMS_baseURL + '\', \'' + accessToken + '\', \'' + ratingKey + '\', \'' + posterURL.replace("&", "&amp;") + '\');atv.unloadPage();">';
    if (posterURL.indexOf('library') !== -1)
      xml = xml + ' \
                  <title>' + title + '</title> \
                  <image>' + PMS_baseURL + posterThumb + '</image>';
    else if (posterURL.indexOf('movieposterdb') !== -1)
      xml = xml + ' \
                  <title>' + title + '</title> \
                  <image>' + posterURL.replace("&","&amp;") + '</image>';
    else
      xml = xml + ' \
                  <title>' + title + '</title> \
                  <image>' + PMS_baseURL + posterThumb + '</image>';
    
    xml = xml + ' \
                  <defaultImage>resource://Poster.png</defaultImage> \
                </goldenPoster>';
	};
	xml = xml + ' \
              </items> \
            </shelfSection> \
          </sections> \
        </shelf> \
        <collectionDivider alignment="left"> \
          <title></title> \
        </collectionDivider> \
      </items> \
    </scroller> \
  </body> \
</atv>';
	var menuDoc = atv.parseXML(xml);
	atv.loadXML(menuDoc);
};

/*
 * Update Plex library with new artwork
 */
function loadNewArtwork(PMS_baseURL, accessToken, ratingKey, posterURL)
{
	if (posterURL.indexOf('library') !== -1)
	{
		var urlParts = posterURL.split('=');
		posterURL = urlParts[1];
	}
    else
    {
        posterURL = encodeURIComponent(posterURL);
    }
    
    var url = PMS_baseURL + "/library/metadata/" + ratingKey + "/poster?url=" + posterURL;
    if (accessToken!='')
        url = url + '&X-Plex-Token=' + accessToken;
    
  var req = new XMLHttpRequest();
	req.open('PUT', url, false);
	req.send();
};
