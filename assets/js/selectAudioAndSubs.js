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
if(atv.Element)
{
	atv.Element.prototype.getElementsByTagName = function(tagName)
	{
		return this.ownerDocument.evaluateXPath("descendant::" + tagName, this);
	};

	atv.Element.prototype.getElementByTagName = function(tagName)
	{
		var elements = this.getElementsByTagName(tagName);
		if(elements && elements.length > 0)
		{
			return elements[0];
		};
		return undefined;
	};
};

var fVer = 60.0; // force old menu till apple fixes the bugs

/*
 * Build Audio/Subtitle menu
 */
var contextDoc;
function selectAudioAndSubs(PMS_baseURL, accessToken, ratingKey) 
{
  fv = atv.device.softwareVersion.split(".");
  firmVer = fv[0] + "." + fv[1];
  if (parseFloat(firmVer) < fVer)
  {
    var xmlstr =
    "<?xml version=\"1.0\" encoding=\"UTF-8\"?> \
    <atv> \
      <head> \
        <script src=\"{{URL(/js/selectAudioAndSubs.js)}}\"/> \
      </head> \
      <body> \
      <optionDialog id=\"optionDialog\"> \
        <header> \
          <simpleHeader> \
            <title>{{TEXT(Select Tracks)}}</title> \
          </simpleHeader> \
        </header> \
        <menu> \
          <sections> \
            <menuSection> \
              <header> \
                <horizontalDivider alignment=\"center\"> \
                  <title>{{TEXT(Audio Track)}}</title> \
                </horizontalDivider> \
              </header> \
              <items>";
      var audioStr = "";
      var subsStr = "";
      var subsDivider = "{{TEXT(Subtitle Track)}}";
      var subsAlign = "center";
  }
  else
  {
    var xmlstr =
    "<?xml version=\"1.0\" encoding=\"UTF-8\"?> \
    <atv> \
      <body> \
      <popUpMenu id=\"popUpMenu\"> \
        <sections> \
          <menuSection> \
            <items>";
    var audioStr = "{{TEXT(Audio)}} - ";
    var subsStr = "{{TEXT(Subs)}} - ";
    var subsDivider = "";
    var subsAlign = "right";
  }
  
	var streams = document.evaluateXPath('//stream');
  
  for(var i = 0; i < streams.length; ++i)
	{
    var stream = streams[i]
    if (stream.getElementByTagName('streamType').textContent == '2')
    { 
      xmlstr = xmlstr + "\
                <oneLineMenuItem id=\"audio" + i.toString() + "\" onSelect=\"selectAudioStream(\'" + PMS_baseURL + "\', \'" + accessToken + "\', \'" + ratingKey + "\', " + stream.getElementByTagName('id').textContent + "); toggleAudioCheck(\'" + i.toString() + "\')\"> \
                <label>" + audioStr + stream.getElementByTagName('language').textContent + " (" + stream.getElementByTagName('codec').textContent + ")</label>";
      if (stream.getElementByTagName('selected').textContent == '1')
      {
        xmlstr = xmlstr + " \
                <accessories> \
                  <checkMark/> \
                </accessories>";
      }
      xmlstr = xmlstr + " \
              </oneLineMenuItem>";
    }
  }
  xmlstr = xmlstr + " \
            </items> \
          </menuSection> \
          <menuSection> \
            <header> \
              <horizontalDivider alignment=\"" + subsAlign + "\"> \
                <title>" + subsDivider + "</title> \
              </horizontalDivider> \
            </header> \
            <items>";
  xmlstr = xmlstr + " \
              <oneLineMenuItem id=\"sub99\" onSelect=\"selectSubStream(\'" + PMS_baseURL + "\', \'" + accessToken + "\', \'" + ratingKey + "\', 0); toggleSubCheck(\'99\')\"> \
                <label>" + subsStr + "{{TEXT(None)}}</label>";
	
	var noSubs = true;
	var noSubsSelected = true;
	for(var i = 0; i < streams.length; ++i)
	{
		if (streams[i].getElementByTagName('streamType').textContent == '3') noSubs = false;
		if  ((streams[i].getElementByTagName('streamType').textContent == '3')&& 
				(streams[i].getElementByTagName('selected').textContent == '1')) noSubsSelected = false;
	}
	if ((noSubs)||(noSubsSelected))
	  xmlstr = xmlstr + " \
                <accessories> \
                  <checkMark/> \
                </accessories>";
		
	xmlstr = xmlstr + " \
              </oneLineMenuItem>";
	
	for(var i = 0; i < streams.length; ++i)
	{
    var stream = streams[i]
    if (stream.getElementByTagName('streamType').textContent == '3')
    { 
      xmlstr = xmlstr + " \
              <oneLineMenuItem id=\"sub" + i.toString() + "\" onSelect=\"selectSubStream(\'" + PMS_baseURL + "\', \'" + accessToken + "\', \'" + ratingKey + "\', " + stream.getElementByTagName('id').textContent + "); toggleSubCheck(\'" + i.toString() + "\')\"> \
                <label>" + subsStr + stream.getElementByTagName('language').textContent + " (" + stream.getElementByTagName('format').textContent + ")</label>";
			if (stream.getElementByTagName('selected').textContent == '1')
			{
				xmlstr = xmlstr + " \
                <accessories> \
                  <checkMark/> \
                </accessories>";
			}
      xmlstr = xmlstr + " \
              </oneLineMenuItem>";
    }
  }
	
  if (parseFloat(firmVer) < fVer)
  {
    xmlstr = xmlstr + " \
                </items> \
              </menuSection> \
            </sections> \
          </menu> \
        </optionDialog> \
      </body> \
    </atv>";  
    var doc = atv.parseXML(xmlstr);
    atv.loadXML(doc);
  }
  else
  {
    xmlstr = xmlstr + " \
                </items> \
              </menuSection> \
            </sections> \
          </popUpMenu> \
        </body> \
      </atv>";
    contextDoc = atv.parseXML(xmlstr);
    atv.contextMenu.load(contextDoc);
  }
	
};	

/*
 * Toggle Subtitle check marks
 */
function toggleSubCheck(id) 
{	
	id = 'sub' + id
  fv = atv.device.softwareVersion.split(".");
  firmVer = fv[0] + "." + fv[1];
  if (parseFloat(firmVer) < fVer)
  {
    var root = document.rootElement;
  }
  else
  {
    var root = contextDoc.rootElement;
  }
	var menuItems = root.getElementsByTagName('oneLineMenuItem');
	if (menuItems)
	{
		// remove old checks
		for(var i = 0; i < menuItems.length; ++i)
		{
			var menuItem = menuItems[i];
			var menuID = menuItem.getAttribute('id')
			if (menuID.indexOf('sub') !== -1)
			{
				var accessories = menuItem.getElementByTagName('accessories');
				if ( accessories )
				{
					accessories.removeFromParent();
				}
			}
		}
		// create new check
		for(var i = 0; i < menuItems.length; ++i)
		{
			var menuItem = menuItems[i];
			var menuID = menuItem.getAttribute('id')
			if ((menuID.indexOf('sub') !== -1)&&(menuID == id))
			{
        addCheckMark(menuItem);
			}
		}
	}
};

/*
 * Toggle Audio check marks
 */
function toggleAudioCheck(id) 
{	
	id = 'audio' + id
  fv = atv.device.softwareVersion.split(".");
  firmVer = fv[0] + "." + fv[1];
  if (parseFloat(firmVer) < fVer)
  {
    var root = document.rootElement;
  }
  else
  {
    var root = contextDoc.rootElement;
  }
	var menuItems = root.getElementsByTagName('oneLineMenuItem');
	if (menuItems)
	{
		// remove old checks
		for(var i = 0; i < menuItems.length; ++i)
		{
			var menuItem = menuItems[i];
			var menuID = menuItem.getAttribute('id')
			if (menuID.indexOf('audio') !== -1)
			{
				var accessories = menuItem.getElementByTagName('accessories');
				if ( accessories )
				{
					accessories.removeFromParent();
				}
			}
		}
		// create new check
		for(var i = 0; i < menuItems.length; ++i)
		{
			var menuItem = menuItems[i];
			var menuID = menuItem.getAttribute('id')
			if ((menuID.indexOf('audio') !== -1)&&(menuID == id))
			{
        addCheckMark(menuItem);
			}
		}
	}
};

// Add Check Mark
function addCheckMark(menuItem)
{
  fv = atv.device.softwareVersion.split(".");
  firmVer = fv[0] + "." + fv[1];
  if (parseFloat(firmVer) < fVer)
  {
    var accessories = document.makeElementNamed("accessories");
    var checkmark = document.makeElementNamed("checkMark");
    accessories.appendChild(checkmark);
    menuItem.appendChild(accessories);
  }
  else
  {
    var accessories = contextDoc.makeElementNamed("accessories");
    var checkmark = contextDoc.makeElementNamed("checkMark");
    accessories.appendChild(checkmark);
    menuItem.appendChild(accessories);
  }
};
 
/*
 * Tell PMS which sub/audio stream to use
 */
function selectSubStream(PMS_baseURL, accessToken, ratingKey, stream) {
    var url = PMS_baseURL + "/library/parts/" + ratingKey + "?subtitleStreamID=" + stream.toString()
    if (accessToken!='')
        url = url + '&X-Plex-Token=' + accessToken;
    
  var req = new XMLHttpRequest();
	req.open('PUT', url, true);
	req.send();
};

function selectAudioStream(PMS_baseURL, accessToken, ratingKey, stream) {
    var url = PMS_baseURL + "/library/parts/" + ratingKey + "?audioStreamID=" + stream.toString()
    if (accessToken!='')
        url = url + '&X-Plex-Token=' + accessToken;
    
  var req = new XMLHttpRequest();
	req.open('PUT', url, true);
	req.send();
};
