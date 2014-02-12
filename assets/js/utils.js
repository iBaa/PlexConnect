
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
 * refresh section
 */
// todo: check for owned/shared
// today: shared servers shouldn't be triggered for refresh, should they?
var refreshSectionElem = [];
var refreshSectionTimer = [];

function refreshSection(id, refreshKey)
{
    setLabel = function(elem, label, text)
    {
        if (!elem.getElementByTagName(label))
        {
            elem_add = document.makeElementNamed(label);
            elem.appendChild(elem_add);
        }
        elem.getElementByTagName(label).textContent = text;
    };
    
    showPict = function(elem, pict)
    {
        var elem_add;
        if (!elem.getElementByTagName("accessories"))
        {
            elem_add = document.makeElementNamed("accessories");
            elem.appendChild(elem_add);
        }
        elem_add = document.makeElementNamed(pict);
        elem.getElementByTagName("accessories").appendChild(elem_add);
    };
    
    hidePict = function(elem, pict)
    {
        var elem_remove = elem.getElementByTagName("accessories").getElementByTagName(pict);
        if (!elem_remove) return undefined;  // error - element not found
        elem_remove.removeFromParent();
    };
    
    checkRefresh = function()
    {
        var timer = refreshSectionTimer.shift()
        var elem = refreshSectionElem.shift()
        
        // todo: check PMS XML for "refreshing=1", then stop timer and hide spinner
        // today: just reset spinner -> setTimeout() would be easier
        atv.clearInterval(timer);  // stop timer
        setLabel(elem, 'rightLabel', '');
        hidePict(elem, 'spinner');
    };
    
    // add spinner
    var elem = document.getElementById(id);
    if (!elem) return;  // error - element not found
    setLabel(elem, 'rightLabel', "{{TEXT(refreshing)}}");
    showPict(elem, 'spinner');
    
    // check status every 10sec
    refreshSectionElem.push(elem);
    refreshSectionTimer.push(atv.setInterval(checkRefresh, 10000));
    
    // request refresh
    var req = new XMLHttpRequest();
    req.open('PUT', refreshKey, false);
    req.send();
}



/*
 * navigation bar - dynamic loading of manu pages
 */
function loadMenuPage(event)
{
    var id = event.navigationItemId;
    log("loadItem: "+id);
    var item = document.getElementById(id);
    var url = item.getElementByTagName('url').textContent;
    
    if (url.indexOf("{{URL()}}")!=-1)
    {
        url = url + "&PlexConnectUDID=" + atv.device.udid;
    }
    
    var req = new XMLHttpRequest();
    req.onreadystatechange = function()
    {
        try
        {
            if(req.readyState == 4)
            {
                doc = req.responseXML
                if(event) event.success(doc);
                else atv.loadXML(doc);
            }
        }
        catch(e)
        {
            req.abort();
        }
    }
    req.open('GET', url, true);
    req.send();
};



/*
 * lookup movie title on tmdb and pass trailer ID to PlexConnect
 */
function playTrailer(title,year)
{
    log("playTrailer: "+title);

    var api_key = "0dd32eece72fc9640fafaa5c87017fcf";
    var lookup = "http://api.themoviedb.org/3/search/movie?api_key="+api_key+"&query="+encodeURIComponent(title)+"&year="+encodeURIComponent(year);
    var doc = JSON.parse(ajax(lookup));
    if (doc.total_results === 0)
    {
        XML_Error("{{TEXT(PlexConnect)}}", "{{TEXT(TheMovieDB: No Trailer Info available)}}");
        return;
    }
    lookup = "http://api.themoviedb.org/3/movie/"+doc.results[0].id+"/trailers?api_key="+api_key;
    doc = JSON.parse(ajax(lookup));
    if (doc.youtube.length === 0)
    {
        XML_Error("{{TEXT(PlexConnect)}}", "{{TEXT(TheMovieDB: No Trailer Info available)}}");
        return;
    }

    var id = doc.youtube[0].source;
    var url = "{{URL(/)}}&PlexConnect=PlayTrailer&PlexConnectTrailerID="+id
    atv.loadURL(url);
};



/*
 *  Small synchronous AJAX handler
 */
function ajax(url)
{
    var req = new XMLHttpRequest();
    req.open('GET', url, false);
    req.send();
    if(req.status == 200) return req.responseText;
}



/*
 * displays error message
 */
function XML_Error(title,desc)
{
    var errorXML =
"<?xml version=\"1.0\" encoding=\"UTF-8\"?> \
<atv> \
    <body> \
        <dialog id=\"com.sample.error-dialog\"> \
            <title>" + title + "</title> \
            <description>" + desc + "</description> \
        </dialog> \
    </body> \
</atv>";
    var doc = atv.parseXML(errorXML);
    atv.loadXML(doc); 
};



/*
 * override stock atv.loadURL() function, adding UDID if directed to PlexConnect
 */
var iOS_atv_loadURL = atv.loadURL;

atv.loadURL = function(url)
{
    log("loadURL (override): "+url);
    if (url.indexOf("{{URL()}}")!=-1)
    {
        url = url + "&PlexConnectUDID=" + atv.device.udid;
        url = url + "&PlexConnectATVName=" + encodeURIComponent(atv.device.displayName);
    }
    
    iOS_atv_loadURL(url);
};



/*
 * override stock atv.loadAndSwapURL() function, adding UDID if directed to PlexConnect
 */
var iOS_atv_loadAndSwapURL = atv.loadAndSwapURL;

atv.loadAndSwapURL = function(url)
{
    log("loadAndSwapURL (override): "+url);
    if (url.indexOf("{{URL()}}")!=-1)
    {
        url = url + "&PlexConnectUDID=" + atv.device.udid;
        url = url + "&PlexConnectATVName=" + encodeURIComponent(atv.device.displayName);
    }
    
    iOS_atv_loadAndSwapURL(url);
};

/*
 * Flatten TV Seasons
 * If show has only one season then flatten it!
 */

flattenSeason = function(url, accessToken, flatten)
{
  if (accessToken!='')
  {
    if (url.indexOf('?') != -1)
    {
      accessToken = '&X-Plex-Token=' + accessToken;
    }
    else
    {
      accessToken = '?X-Plex-Token=' + accessToken;
    }
  }

  if (flatten=='False') 
  {
    atv.loadURL(url);
  }
  else
  {
    var urlparts = url.split('(')
    var newurl = urlparts[1].replace(')','');

    var req = new XMLHttpRequest();
    req.onreadystatechange = function()
    {
      try
      {
        if(req.readyState == 4)
        {
          doc = req.responseXML;
          root = doc.rootElement;
          var size = root.getAttribute('size');
          if (size=='1')
          {
            var newpath = root.getElementByTagName('Directory').getAttribute('key');
            urlparts = url.split('/library');
            newurl = urlparts[0] + newpath;
            atv.loadURL(newurl);
          }
          else if (size=='2')
          {
            var newpaths = root.getElementsByTagName('Directory');
            var newpath = newpaths[1].getAttribute('key');
            urlparts = url.split('/library');
            newurl = urlparts[0] + newpath;
            atv.loadURL(newurl);
          }
          else
          {
            atv.loadURL(url);
          } 
        }
      }
      catch(e)
      {
        req.abort();
      }
    }
    req.open('GET', unescape(newurl) + accessToken, true);
    req.send();
  }
}


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
 * Update Plex library with new artwork
 */
function changeArtwork(PMS_baseURL, accessToken, ratingKey, posterURL, shelf)
{
  if (shelf != '')
  {
    // Selector logic for Show/Season level artwork
    var root = document.rootElement;
    var shelf = document.getElementById(shelf);
    if (shelf == null) return;
    var items = shelf.getElementsByTagName('moviePoster');
    if (items == null) return;
  
    for (var i=0; i<items.length; i++)
    {
      if (items[i].getAttribute('id') == posterURL) 
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
  if (accessToken!='') url = url + '&X-Plex-Token=' + accessToken;
    
  var req = new XMLHttpRequest();
	req.open('PUT', url, true);
	req.send();
};
