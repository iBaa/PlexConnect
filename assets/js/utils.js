
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
function playTrailer(addrPMS,title,year)
{
    log("playTrailer: "+title);

    var api_key = "0dd32eece72fc9640fafaa5c87017fcf";
    var lookup = "http://api.themoviedb.org/3/search/movie?api_key="+api_key+"&query="+encodeURIComponent(title)+"&year="+encodeURIComponent(year);
    var req = new XMLHttpRequest();
    req.onreadystatechange = function()
    {
        try
        {
            if(req.readyState == 4)
            {
                var doc = JSON.parse(req.responseText);

                if (doc.total_results === 0)
                {
                    XML_Error('PlexConnect: Trailer Lookup', 'Movie Not Found');
                    return;
                } 

                var lookup2 = "http://api.themoviedb.org/3/movie/"+doc.results[0].id+"/trailers?api_key="+api_key;
                var req2 = new XMLHttpRequest();
                req2.onreadystatechange = function()
                {
                    try
                    {
                        if(req2.readyState == 4)
                        {
                            var doc2 = JSON.parse(req2.responseText);

                            if (doc2.youtube.length === 0)
                            {
                                XML_Error('PlexConnect: Trailer Lookup', 'YouTube Trailer Not Found');
                                return;
                            }

                            var video = doc2.youtube[0].source;
                            var url = "http://atv.plexconnect/system/services/url/lookup?url=http%3A//www.youtube.com/watch%3Fv%3D"+encodeURIComponent(video)+"&PlexConnect=Play";

                            atv.loadURL(url);

                        }
                    }
                    catch(e)
                    {
                        req2.abort();
                    }
                }
                req2.open('GET', lookup2, true);
                req2.send();
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
 * displays error message
 */
function XML_Error(title,desc)
{
    var errorXML =
'<?xml version="1.0" encoding="UTF-8"?> \
<atv> \
    <body> \
        <dialog id="com.sample.error-dialog"> \
            <title>' + title + '</title> \
            <description>' + desc + '</description> \
        </dialog> \
    </body> \
</atv>';
    var doc = atv.parseXML(errorXML);
    atv.loadXML(doc); 
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