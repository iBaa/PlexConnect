
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
    var url = "http://atv.plexconnect/" + "&PlexConnectLog=" + encodeURIComponent(msg);
    req.open('GET', url, true);
    req.send();
};



/*
 * navigation bar - dynamic loading of manu pages
 */
function loadMenuPage(event)
{
    var id = event.navigationItemId;
    log("loadItem: "+id);
    var item = document.getElementById(id);
    var url = item.getElementByTagName('url').textContent;
    
    if (url.toLowerCase().indexOf("atv.plexconnect")!=-1)
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

atv.showDialog = function(message, description)
{
    var dialogXML = '<?xml version="1.0" encoding="UTF-8"?> \
                    <atv> \
                    <body> \
                    <dialog id="com.plexconnect.dialog"> \
                    <title><![CDATA[' + message + ']]></title> \
 	            <description><![CDATA[' + description + ']]></description> \
                    </dialog> \
                    </body> \
                    </atv>';
 
    atv.loadXML(atv.parseXML(dialogXML));
};
 
atv.showInputTextPage = function(input_type, input_title, input_instructions, callback, defaultvalue)
{
    var textEntry = new atv.TextEntry();
    textEntry.type = input_type;
    textEntry.title = input_title;
    textEntry.instructions = input_instructions;
    textEntry.defaultValue = defaultvalue;
    textEntry.onSubmit = callback;
    textEntry.show();
};

function testval(keyword)
{
    atv.showDialog("test", keyword);
};

/*
 * override stock atv.loadURL() function, adding UDID if directed to PlexConnect
 */
var iOS_atv_loadURL = atv.loadURL;

atv.loadURL = function(url)
{
    log("loadURL (override): "+url);
    if (url.indexOf("atv.plexconnect")!=-1)
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
    if (url.indexOf("atv.plexconnect")!=-1)
    {
        url = url + "&PlexConnectUDID=" + atv.device.udid;
        url = url + "&PlexConnectATVName=" + encodeURIComponent(atv.device.displayName);
    }
    
    iOS_atv_loadAndSwapURL(url);
};

atv.show