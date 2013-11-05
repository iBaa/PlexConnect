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

/*
 * Build Audio/Subtitle menu
 */
function selectAudioAndSubs(PMS_baseURL, accessToken, ratingKey) {
  var xmlstr =
'<?xml version="1.0" encoding="UTF-8"?> \
<atv> \
  <head> \
    <script src="http://atv.plexconnect/js/selectAudioAndSubs.js"/> \
  </head> \
  <body> \
    <optionDialog id="optionDialog"> \
      <header> \
        <simpleHeader> \
          <title>{{TEXT(Select Tracks)}}</title> \
        </simpleHeader> \
      </header> \
      <menu> \
        <sections> \
          <menuSection> \
            <header> \
              <horizontalDivider alignment="center"> \
                <title>{{TEXT(Audio Track)}}</title> \
              </horizontalDivider> \
            </header> \
            <items>';

	var streams = document.evaluateXPath('//stream');
  
  for(var i = 0; i < streams.length; ++i)
	{
    var stream = streams[i]
    if (stream.getElementByTagName('streamType').textContent == '2')
    { 
      xmlstr = xmlstr + '\
                <oneLineMenuItem id="audio' + i.toString() + '" onSelect="selectAudioStream(\'' + PMS_baseURL + '\', \'' + accessToken + '\', \'' + ratingKey + '\', ' + stream.getElementByTagName('id').textContent + '); toggleAudioCheck(\'' + i.toString() + '\')"> \
                <label>' + stream.getElementByTagName('language').textContent + ' (' + stream.getElementByTagName('codec').textContent + ')</label>';
      if (stream.getElementByTagName('selected').textContent == '1')
      {
        xmlstr = xmlstr + ' \
                <accessories> \
                  <checkMark/> \
                </accessories>';
      }
      xmlstr = xmlstr + ' \
              </oneLineMenuItem>';
    }
  }
  xmlstr = xmlstr + ' \
            </items> \
          </menuSection> \
          <menuSection> \
            <header> \
              <horizontalDivider alignment="center"> \
                <title>{{TEXT(Subtitle Track)}}</title> \
              </horizontalDivider> \
            </header> \
            <items>';
  xmlstr = xmlstr + ' \
              <oneLineMenuItem id="sub99" onSelect="selectSubStream(\'' + PMS_baseURL + '\', \'' + accessToken + '\', \'' + ratingKey + '\', 0); toggleSubCheck(\'99\')"> \
                <label>{{TEXT(None)}}</label>';
	
	var noSubs = true;
	var noSubsSelected = true;
	for(var i = 0; i < streams.length; ++i)
	{
		if (streams[i].getElementByTagName('streamType').textContent == '3') noSubs = false;
		if  ((streams[i].getElementByTagName('streamType').textContent == '3')&& 
				(streams[i].getElementByTagName('selected').textContent == '1')) noSubsSelected = false;
	}
	if ((noSubs)||(noSubsSelected))
	  xmlstr = xmlstr + ' \
                <accessories> \
                  <checkMark/> \
                </accessories>';
		
	xmlstr = xmlstr + ' \
              </oneLineMenuItem>';
	
	for(var i = 0; i < streams.length; ++i)
	{
    var stream = streams[i]
    if (stream.getElementByTagName('streamType').textContent == '3')
    { 
      xmlstr = xmlstr + ' \
              <oneLineMenuItem id="sub' + i.toString() + '" onSelect="selectSubStream(\'' + PMS_baseURL + '\', \'' + accessToken + '\', \'' + ratingKey + '\', ' + stream.getElementByTagName('id').textContent + '); toggleSubCheck(\'' + i.toString() + '\')"> \
                <label>' + stream.getElementByTagName('language').textContent + ' (' + stream.getElementByTagName('format').textContent + ')</label>';
			if (stream.getElementByTagName('selected').textContent == '1')
			{
				xmlstr = xmlstr + ' \
                <accessories> \
                  <checkMark/> \
                </accessories>';
			}
      xmlstr = xmlstr + ' \
              </oneLineMenuItem>';
    }
  }
	
	xmlstr = xmlstr + ' \
            </items> \
          </menuSection> \
        </sections> \
      </menu> \
    </optionDialog> \
  </body> \
</atv>';
  var doc = atv.parseXML(xmlstr);
  atv.loadXML(doc);	
};	

/*
 * Toggle Subtitle check marks
 */
function toggleSubCheck(id) 
{	
	id = 'sub' + id
	var root = document.rootElement;
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
				var accessories = document.makeElementNamed("accessories");
        var checkmark = document.makeElementNamed("checkMark");
        accessories.appendChild(checkmark);
        menuItem.appendChild(accessories);
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
	var root = document.rootElement;
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
				var accessories = document.makeElementNamed("accessories");
        var checkmark = document.makeElementNamed("checkMark");
        accessories.appendChild(checkmark);
        menuItem.appendChild(accessories);
			}
		}
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
