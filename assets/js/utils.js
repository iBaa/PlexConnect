
// atv.Document extensions
if( atv.Document ) {
    atv.Document.prototype.getElementById = function(id) {
        var elements = this.evaluateXPath("//*[@id='" + id + "']", this);
        if ( elements && elements.length > 0 ) {
            return elements[0];
        }
        return undefined;
    }   
}


// atv.Element extensions
if( atv.Element ) {
    atv.Element.prototype.getElementsByTagName = function(tagName) {
        return this.ownerDocument.evaluateXPath("descendant::" + tagName, this);
    }

    atv.Element.prototype.getElementByTagName = function(tagName) {
        var elements = this.getElementsByTagName(tagName);
        if ( elements && elements.length > 0 ) {
            return elements[0];
        }
        return undefined;
    }
}


// string extension: format()
// see http://stackoverflow.com/a/4673436
if (!String.prototype.format) {
  String.prototype.format = function() {
    var args = arguments;
    return this.replace(/{(\d+)}/g, function(match, number) { 
      return typeof args[number] != 'undefined' ? args[number] : match;
    });
  };
}


/*
 * ATVLogger
 */
function log(msg, level)
{
    level = level || 1;
    var req = new XMLHttpRequest();
    var url = "{{URL(/)}}" + "&PlexConnectATVLogLevel=" + level.toString() + "&PlexConnectLog=" + encodeURIComponent(msg);
    req.open('GET', url, true);
    req.send();
};

/*
 * Mark a item watched or unwatched
 * Pass action as scrobble or unscrobble 
 */
function markItem(PMS_baseURL, accessToken, ratingKey, action)
{
  var url = PMS_baseURL + "/:/" + action + "?key=" + ratingKey + "&identifier=com.plexapp.plugins.library";
  if (accessToken!='') url = url + '&X-Plex-Token=' + accessToken;
    
	var req = new XMLHttpRequest();
	req.open('GET', url, false);
	req.send();
}

/*
 * Delete an item from the library
 */
function deleteItem(PMS_baseURL, accessToken, ratingKey)
{
  var url = PMS_baseURL + "/library/metadata/" + ratingKey;
  if (accessToken!='') url = url + '?X-Plex-Token=' + accessToken;
    
	var req = new XMLHttpRequest();
	req.open('DELETE', url, false);
	req.send();
}

/*
 * Update Plex library with new artwork
 */
function changeArtwork(PMS_baseURL, accessToken, ratingKey, artURL, shelfName)
{
  if (shelfName != '' && shelfName != 'fanart')
  {
    // Selector logic for Show/Season level artwork
    var root = document.rootElement;
    var shelf = document.getElementById(shelfName);
    if (shelf == null) return;
    var items = shelf.getElementsByTagName('moviePoster');
    if (items == null) return;
  
    for (var i=0; i<items.length; i++)
    {
      if (items[i].getAttribute('id') == artURL) 
      {
      items[i].getElementByTagName('title').textContent = "Selected";
      }
      else
      { 
        items[i].getElementByTagName('title').textContent = "";
      }
    }
  }
  
  // Test if art is from library or external location
  if (artURL.indexOf('library') !== -1)
	{
		var urlParts = artURL.split('=');
		artURL = urlParts[1];
	}
   else
  {
    artURL = encodeURIComponent(artURL);
  }
  
  if (shelfName != 'fanart')
  {
    var url = PMS_baseURL + "/library/metadata/" + ratingKey + "/poster?url=" + artURL;
  }
  else
  {
    var url = PMS_baseURL + "/library/metadata/" + ratingKey + "/art?url=" + artURL;
  }
  if (accessToken!='') url = url + '&X-Plex-Token=' + accessToken;
    
  var req = new XMLHttpRequest();
	req.open('PUT', url, true);
	req.send();
};

/*
 * ScrobbleMenu
 */
 function scrobbleMenu(url)
{
  fv = atv.device.softwareVersion.split(".");
  firmVer = fv[0] + "." + fv[1];
  log(firmVer);
  if (parseFloat(firmVer) < 6.0)
  {
    // firmware <6.0
    // load standard scrobble menu
    atv.loadURL(url);
  }
  else
  {
    // firmware >=6.0
    // load scrobble menu xml
    // parse the xml and build a popup context menu 
    var url = url + "&PlexConnectUDID="+atv.device.udid
    var req = new XMLHttpRequest();
    req.onreadystatechange = function()
    {
      try
      {
        if(req.readyState == 4)
        {
          xml = req.responseText;
          if(xml.indexOf('popUpMenu') !== -1)
          {
            xmlDoc = atv.parseXML(xml);
            atv.contextMenu.load(xmlDoc);
          }
          else
          {
            xmlDoc = atv.parseXML(xml);
            atv.loadXML(xmlDoc);
          }
          xmlDoc = atv.parseXML(xml);
          atv.contextMenu.load(xmlDoc);
        } 
      }
      catch(e)
      {
        req.abort();
      }
    }
    
    req.open('GET',unescape(url), false);
    req.send();
  }
}

/*
 * xml updater Major Hack :)
 */
function updateContextXML()
{
  xmlstr = '<atv><body><optionList id="fakeUpdater" autoSelectSingleItem="true"> \
            <items><oneLineMenuItem id="0" onSelect="atv.unloadPage()"><label></label> \
            </oneLineMenuItem></items></optionList></body></atv>';
  xmlDoc = atv.parseXML(xmlstr);
  atv.loadXML(xmlDoc);
}
