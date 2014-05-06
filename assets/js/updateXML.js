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
 * navigation bar - dynamic loading of pages
 */
 
var navbarID = null;
var navbarItemNumber = null;
 
function loadItem(event)
{
  // Get navbar item id name and number
  navbarID = event.navigationItemId;
  var root = document.rootElement;
  var navitems = root.getElementsByTagName('navigationItem')
  for (var i=0;i<navitems.length;i++)
  { 
    if (navitems[i].getAttribute('id') == navbarID) 
    {
      navbarItemNumber = i.toString();
      break;
    }
  }
  log(navbarItemNumber);
  log(navbarID);

  // Get navbar item URL
	var item = document.getElementById(navbarID);
  var url = item.getElementByTagName('url').textContent;
  if (url.indexOf("{{URL(/)}}")!=-1)
  {
    url = url + "&PlexConnectUDID=" + atv.device.udid;
    url = url + "&PlexConnectATVName=" + encodeURIComponent(atv.device.displayName);
  }
  loadMenuPages(url, event);
};


function loadMenuPages(url, event)
{
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
 * Update page
 */
function updatePage(url)
{
  // add UDID
  if (url.indexOf("{{URL(/)}}")!=-1)
  {
    url = url + "&PlexConnectUDID=" + atv.device.udid;
  }
  
  // read new XML
	if (navbarItemNumber == '1') // First navbar item is a special case
	{
		atv.loadAndSwapURL(url);
	}
	else
	{
		var req = new XMLHttpRequest();
		req.onreadystatechange = function(){
			if(req.readyState == 4)
			{
				var doc = req.responseXML;
				var navBar = doc.getElementById('PlexConnect_Navigation');
				var navKey = navBar.getElementByTagName('navigation');
				navKey.setAttribute('currentIndex', navbarItemNumber);
				atv.loadAndSwapXML(doc);
			}
		};
	};
  req.open('GET', url, false);
  req.send();
};
