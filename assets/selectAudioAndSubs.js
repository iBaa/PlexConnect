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
 * ATVLogger
 */
function log(msg)
{
    msg = msg.replace(/ /g, "%20")
    msg = msg.replace(/</g, "&lt;")
    msg = msg.replace(/>/g, "&gt;")
    msg = msg.replace(/\//g, "&fs;")
    msg = msg.replace(/"/g, "&qo;")
		var req = new XMLHttpRequest();
		var url = "http://trailers.apple.com/" + msg + "&atvlogger";
		req.open('GET', url, true);
		req.send();
};

/*
 * Build Audio/Subtitle menu
 */
function selectAudioAndSubs(addrPMS, ratingKey, pmsPath) {
	// Load PMS metadata xml
	var url = "http://" + addrPMS + pmsPath;
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
	
	var xmlstr = '<?xml version="1.0" encoding="UTF-8"?><atv><head><script src="http://trailers.apple.com/selectAudioAndSubs.js"/></head> \
                <body><optionDialog id="optionDialog"><header><simpleHeader><title>Select Tracks</title></simpleHeader></header> \
								<menu><sections><menuSection><header><horizontalDivider alignment="center"><title>Audio Track</title></horizontalDivider> \
								</header><items>';

	var streams = doc.evaluateXPath('descendant::Stream');

  for(var i = 0; i < streams.length; ++i)
	{
    var stream = streams[i]
		var selected = stream.getAttribute('selected');
		if (!selected) selected = "0";
    if (stream.getAttribute('streamType') == '2')
    { 
      xmlstr = xmlstr + '<oneLineMenuItem id="audio' + i.toString() + '" onSelect="selectAudioStream(\'' + addrPMS + '\', \'' + ratingKey + '\', ' + stream.getAttribute('id') + '); toggleAudioCheck(\'' + i.toString() + '\')">';
      xmlstr = xmlstr + '<label>' + stream.getAttribute('language') + ' (' + stream.getAttribute('codec') + ')</label>';
			if (selected == '1')
			{
				xmlstr = xmlstr + '<accessories><checkMark/></accessories>';
			}
      xmlstr = xmlstr + '</oneLineMenuItem>';
    }
  }
  xmlstr = xmlstr + '</items></menuSection><menuSection><header><horizontalDivider alignment="center"><title>Subtitle Track</title></horizontalDivider></header><items>';
	xmlstr = xmlstr + '<oneLineMenuItem id="sub99" onSelect="selectSubStream(\'' + addrPMS + '\', \'' + ratingKey + '\', 0); toggleSubCheck(\'99\')"><label>None</label>';

	var noSubs = true;
	var noSubsSelected = true;
	for(var i = 0; i < streams.length; ++i)
	{
		var selected = streams[i].getAttribute('selected');
		if (!selected) selected = "0";
		if (streams[i].getAttribute('streamType') == '3') noSubs = false;
		if  ((streams[i].getAttribute('streamType') == '3')&& 
				(selected == '1')) noSubsSelected = false;
	}
	if ((noSubs)||(noSubsSelected)) xmlstr = xmlstr + '<accessories><checkMark/></accessories>';
		
	xmlstr = xmlstr + '</oneLineMenuItem>';

	for(var i = 0; i < streams.length; ++i)
	{
    var stream = streams[i]
		var selected = stream.getAttribute('selected');
		if (!selected) selected = "0";
    if (stream.getAttribute('streamType') == '3')
    { 
      xmlstr = xmlstr + '<oneLineMenuItem id="sub' + i.toString() + '" onSelect="selectSubStream(\'' + addrPMS + '\', \'' + ratingKey + '\', ' + stream.getAttribute('id') + '); toggleSubCheck(\'' + i.toString() + '\')">';
      xmlstr = xmlstr + '<label>' + stream.getAttribute('language') + ' (' + stream.getAttribute('format') + ')</label>';
			if (selected == '1')
			{
				xmlstr = xmlstr + '<accessories><checkMark/></accessories>';
			}
      xmlstr = xmlstr + '</oneLineMenuItem>';
    }
  }

	xmlstr = xmlstr + '</items></menuSection></sections></menu></optionDialog></body></atv>';
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
function selectSubStream(addrPMS, ratingKey, stream) {
  var url = "http://" + addrPMS + "/library/parts/" + ratingKey + "?subtitleStreamID=" + stream.toString()
  var req = new XMLHttpRequest();
	req.open('PUT', url, true);
	req.send();
};

function selectAudioStream(addrPMS, ratingKey, stream) {
  var url = "http://" + addrPMS + "/library/parts/" + ratingKey + "?audioStreamID=" + stream.toString()
  var req = new XMLHttpRequest();
	req.open('PUT', url, true);
	req.send();
};
