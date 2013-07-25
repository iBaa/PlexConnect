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
		var req = new XMLHttpRequest();
		var url = "http://trailers.apple.com/" + "&PlexConnectLog=" + encodeURIComponent(msg);
		req.open('GET', url, true);
		req.send();
};

/*
 * update Settings
 */
function toggleSettings(opt, template) {
    // get "opt" element of displayed XML
    var dispval = document.getElementById(opt).getElementByTagName("rightLabel");
    if (!dispval) return undefined;  // error - element not found
    
    // read new XML
    var url = "http://trailers.apple.com/&PlexConnect=SettingsToggle:"+ opt + "+" + template + "&PlexConnectUDID="+atv.device.udid
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
