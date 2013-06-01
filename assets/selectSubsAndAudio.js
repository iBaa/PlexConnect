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

function selectSubs(addrPMS, ratingKey) {
  var xmlstr = '<?xml version="1.0" encoding="UTF-8"?><atv><head><script src="http://trailers.apple.com/selectSubsAndAudio.js"/></head> \
                <body><optionList id="selectSubs.optionDialog"><title>Select Subtitle Track</title><items> \
                <oneLineMenuItem id="none" onSelect="selectSubStream(\'' + addrPMS + '\', \'' + ratingKey + '\', 0);atv.unloadPage();"><label>None</label></oneLineMenuItem>';

  var streams = document.evaluateXPath('//stream');
  
  for(var i = 0; i < streams.length; ++i)
	{
    var stream = streams[i]
    if (stream.getElementByTagName('streamType').textContent == '3')
    { 
      xmlstr = xmlstr + '<oneLineMenuItem id="substream" onSelect="selectSubStream(\'' + addrPMS + '\', \'' + ratingKey + '\', ' + stream.getElementByTagName('id').textContent + ');atv.unloadPage();">';
      xmlstr = xmlstr + '<label>' + stream.getElementByTagName('language').textContent + ' (' + stream.getElementByTagName('format').textContent + ')</label>';
      xmlstr = xmlstr + '</oneLineMenuItem>';
    }
  }
  xmlstr = xmlstr + '</items></optionList></body></atv>';
  var doc = atv.parseXML(xmlstr);
  atv.loadXML(doc);
};

function selectAudio(addrPMS, ratingKey) {
  var xmlstr = '<?xml version="1.0" encoding="UTF-8"?><atv><head><script src="http://trailers.apple.com/selectSubsAndAudio.js"/></head> \
                <body><optionList id="selectSubs.optionDialog"><title>Select Audio Track</title><items>';

  var streams = document.evaluateXPath('//stream');
  
  for(var i = 0; i < streams.length; ++i)
	{
    var stream = streams[i]
    if (stream.getElementByTagName('streamType').textContent == '2')
    { 
      xmlstr = xmlstr + '<oneLineMenuItem id="substream" onSelect="selectAudioStream(\'' + addrPMS + '\', \'' + ratingKey + '\', ' + stream.getElementByTagName('id').textContent + ');atv.unloadPage();">';
      xmlstr = xmlstr + '<label>' + stream.getElementByTagName('language').textContent + ' (' + stream.getElementByTagName('codec').textContent + ')</label>';
      xmlstr = xmlstr + '</oneLineMenuItem>';
    }
  }
  xmlstr = xmlstr + '</items></optionList></body></atv>';
  var doc = atv.parseXML(xmlstr);
  atv.loadXML(doc);
};

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
