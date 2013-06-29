function reloadPMS_XML(path) {
  atv.loadAndSwapURL("http://trailers.apple.com" + path);
};




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
    msg = msg.replace(/"/g, "&qo;")
		var req = new XMLHttpRequest();
		var url = "http://trailers.apple.com/" + msg + "&atvlogger";
		req.open('GET', url, true);
		req.send();
};


/*
 * navigation bar - dynamic loading of pages
 */
 
var navbarID = null;
 
function loadItem(event)
{
    navbarID = event.navigationItemId;
		log(navbarID);
		var item = document.getElementById(navbarID);
    var url = item.getElementByTagName('url').textContent;
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
function updatePage(path)
{
	// read new XML
  var url = "http://trailers.apple.com" + path


	if (navbarID == '1') // First navbar item is a special case
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
				navKey.setAttribute('currentIndex', navbarID);
				atv.loadAndSwapXML(doc);
			}
		};
	};
  req.open('GET', url, false);
  req.send();
};
