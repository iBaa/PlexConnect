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
function log(msg)
{
    msg = msg.replace(/ /g, "%20")
    msg = msg.replace(/</g, "&lt;")
    msg = msg.replace(/>/g, "&gt;")
    msg = msg.replace(/\//g, "&fs;")
    
    loadPage("http://trailers.apple.com/" + msg + "&atvlogger");
};

function loadPage(url)
{
	var req = new XMLHttpRequest();
	req.open('GET', url, true);
	req.send();
};

/*
 * update Settings
 */
function toggleSettings(opt) {
    // get "opt" element of displayed XML
    var dispval = document.getElementById(opt).getElementByTagName("rightLabel");
    if (!dispval) return undefined;  // error - element not found
    
    // read new XML
    var url = "http://trailers.apple.com/&PlexConnect=SettingsToggle:"+opt
    var req = new XMLHttpRequest();
    req.open('GET', url, false);
    req.send();
    doc=req.responseXML;
    
    // get "opt" element of fresh XML
    var newval = doc.getElementById(opt).getElementByTagName("rightLabel");
    if (!newval) return undefined;  // error - element not found
    log("new setting - "+opt+"="+newval.textContent);
    
    // push new value to display
    dispval.textContent = newval.textContent;
};

/*
function settings(mode) {
  var item = document.getElementById(mode);
  var value = item.getElementByTagName("rightLabel");
  if (!value) return undefined;
    
  if (mode=="MovieView") {
    if (value.textContent=="Grid") value.textContent = "List";
    else if (value.textContent=="List") value.textContent = "Grid";
  }
  
  if (mode=="ShowView") {
    if (value.textContent=="Grid") value.textContent = "List";
    else if (value.textContent=="List") value.textContent = "Grid";
    //else if (value.textContent=="Bookcase") value.textContent = "Grid";
  }
  
  if (mode=="SeasonView") {
    if (value.textContent=="List") value.textContent = "Coverflow";
    else if (value.textContent=="Coverflow") value.textContent = "List";
  }
  
  rebuildSettingsString();
  loadPage("http://trailers.apple.com/&settings:" + atv.localStorage['PlexConnectSettings']);
};
*/
/*
function createSettingsPage(doc) {
  var item = doc.getElementById("SettingsPage");
  if (!item) return doc;
  item = doc.getElementById("MovieView");
  var value = item.getElementByTagName("rightLabel");
  value.textContent = getSetting("MovieView");
  item = doc.getElementById("ShowView");
  var value = item.getElementByTagName("rightLabel");
  value.textContent = getSetting("ShowView");
  item = doc.getElementById("SeasonView");
  var value = item.getElementByTagName("rightLabel");
  value.textContent = getSetting("SeasonView");
  return doc;
};
*/
/*
function getSetting(name)
{
  var settings = atv.localStorage['PlexConnectSettings'];
  var parts = settings.split(":");
  for (var i=0;i<parts.length;i++)
  {
    if (parts[i] == name) return parts[i+1];
  }
  return '';
};
*/

/*
 * navigation bar - dynamic loading of pages
 */
function loadItem(event)
{
	var id = event.navigationItemId;
  log(id);
  var item = document.getElementById(id);
	var url = item.getElementByTagName('url').textContent;
	loadMenuPages(url, event);
};

/*
function loadDoc(doc, event)
{
  createSettingsPage(doc);
  if(event) event.success(doc);
	else atv.loadXML(doc);
};
*/

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
function rebuildSettingsString()
{
  var setting1 = document.getElementById("MovieView").getElementByTagName("rightLabel").textContent;
  var setting2 = document.getElementById("ShowView").getElementByTagName("rightLabel").textContent;
  var setting3 = document.getElementById("SeasonView").getElementByTagName("rightLabel").textContent;
  var settings = "PlexConnectSettings:MovieView:" + setting1 + ":ShowView:" + setting2 + ":SeasonView:" + setting3;
  settings = settings + ":ForceDirectPlay:false:ForceTranscode:false:TranscoderQuality:9";
  atv.localStorage['PlexConnectSettings'] = settings;
};
*/