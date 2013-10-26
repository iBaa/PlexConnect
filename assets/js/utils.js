
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
function log(msg, level)
{
    level = level || 1;
    var req = new XMLHttpRequest();
    var url = "http://atv.plexconnect/" + "&PlexConnectATVLogLevel=" + level.toString() + "&PlexConnectLog=" + encodeURIComponent(msg);
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



/*
 * translate movie title into trailer URL for playback
 */
function playTrailer(addrPMS,title)
{
    log("playTrailer: "+title);
    var lookup = "https://gdata.youtube.com/feeds/api/videos?q="+encodeURIComponent(title)+"+trailer&start-index=1&max-results=1&v=2&alt=json&hd";

    var req = new XMLHttpRequest();
    req.onreadystatechange = function()
    {
        try
        {
            if(req.readyState == 4)
            {
                var doc = JSON.parse(req.responseText);
                var links = doc.feed.entry[0].link;

                for (var i = 0; i < links.length; i++) {
                    if (links[i].type == "text/html") {
                        var pattern = /watch\?v=(\w+)&/i;
                        var video = pattern.exec(links[i].href)[1];
                        break;
                    }
                };

                var url = "http://atv.plexconnect/PMS("+encodeURIComponent(addrPMS)+")/system/:/services/url/lookup?url=http%3A//www.youtube.com/watch%3Fv%3D"+video+"&PlexConnect=Play";

                if (url.indexOf("atv.plexconnect")!=-1)
                {
                    url = url + "&PlexConnectUDID=" + atv.device.udid;
                    url = url + "&PlexConnectATVName=" + encodeURIComponent(atv.device.displayName);
                }
                
                iOS_atv_loadURL(url);
            }
        }
        catch(e)
        {
            req.abort();
        }
    }
    req.open('GET', lookup, true);
    req.send();
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