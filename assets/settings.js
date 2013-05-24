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

function log(msg)
{
    var strReplaceAll = msg;
    var intIndexOfMatch = strReplaceAll.indexOf(" ");
    while (intIndexOfMatch != -1){
        strReplaceAll = strReplaceAll.replace( " ", "%20" )
        intIndexOfMatch = strReplaceAll.indexOf( " " );
    }
    intIndexOfMatch = strReplaceAll.indexOf("<");
    while (intIndexOfMatch != -1){
        strReplaceAll = strReplaceAll.replace( "<", "&lt;" )
        intIndexOfMatch = strReplaceAll.indexOf( "<" );
    }
    intIndexOfMatch = strReplaceAll.indexOf(">");
    while (intIndexOfMatch != -1){
        strReplaceAll = strReplaceAll.replace( ">", "&gt;" )
        intIndexOfMatch = strReplaceAll.indexOf( ">" );
    }
    intIndexOfMatch = strReplaceAll.indexOf("/");
    while (intIndexOfMatch != -1){
        strReplaceAll = strReplaceAll.replace( "/", "&fs;" )
        intIndexOfMatch = strReplaceAll.indexOf( "/" );
    }
    loadPage("http://trailers.apple.com/" + strReplaceAll + "&atvlogger");
};

function loadPage(url)
{
	var req = new XMLHttpRequest();
	req.open('GET', url, true);
	req.send();
};

function settings(mode) {
  var item = document.getElementById(mode);
  var value = item.getElementByTagName("rightLabel");
  if (!value) return undefined;
    
  if (mode=="MovieView") {
    if (value.textContent=="Grid")
    {
      value.textContent = "List";
    }
    else
    {
      value.textContent = "Grid";
    }
  }
  
  if (mode=="ShowView") {
    if (value.textContent=="Grid")
    {
      value.textContent = "List";
    }
    else
    {
      value.textContent = "Grid";
    }
  }
  rebuildSettingsString();
  loadPage("http://trailers.apple.com/&settings:" + atv.localStorage['PlexConnectSettings']);
};

function createSettingsPage(doc) {
  var item = doc.getElementById("SettingsPage");
  if (!item) return doc;
  item = doc.getElementById("MovieView");
  var value = item.getElementByTagName("rightLabel");
  value.textContent = getSetting("MovieView");
  item = doc.getElementById("ShowView");
  var value = item.getElementByTagName("rightLabel");
  value.textContent = getSetting("ShowView");
  return doc;
};

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

function loadItem(event)
{
	var id = event.navigationItemId;
  log(id);
  var item = document.getElementById(id);
	var url = item.getElementByTagName('url').textContent;
	loadMenuPages(url, event);
};

function loadDoc(doc, event)
{
  createSettingsPage(doc);
  if(event) event.success(doc);
	else atv.loadXML(doc);
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
				loadDoc(req.responseXML , event);
			}
		}
		catch(e)
		{
			req.abort();
		}
	}
	req.open('GET', url, true);
	req.send();
}

function rebuildSettingsString()
{
  var setting1 = document.getElementById("MovieView").getElementByTagName("rightLabel").textContent;
  var setting2 = document.getElementById("ShowView").getElementByTagName("rightLabel").textContent;
  var settings = "PlexConnectSettings:MovieView:" + setting1 + ":ShowView:" + setting2 + ":ForceDirectPlay:false:ForceTranscode:false:TranscoderQuality:9";
  atv.localStorage['PlexConnectSettings'] = settings;
};
