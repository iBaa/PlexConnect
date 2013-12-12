
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
    var url = "{{URL(/)}}" + "&PlexConnectATVLogLevel=" + level.toString() + "&PlexConnectLog=" + encodeURIComponent(msg);
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
    
    if (url.indexOf("{{URL()}}")!=-1)
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
 * lookup movie title on tmdb and pass trailer ID to PlexConnect
 */
function playTrailer(title,year)
{
    log("playTrailer: "+title);

    var api_key = "0dd32eece72fc9640fafaa5c87017fcf";
    var lookup = "http://api.themoviedb.org/3/search/movie?api_key="+api_key+"&query="+encodeURIComponent(title)+"&year="+encodeURIComponent(year);
    var doc = JSON.parse(ajax(lookup));
    if (doc.total_results === 0)
    {
        XML_Error("{{TEXT(PlexConnect)}}", "{{TEXT(TheMovieDB: No Trailer Info available)}}");
        return;
    }
    lookup = "http://api.themoviedb.org/3/movie/"+doc.results[0].id+"/trailers?api_key="+api_key;
    doc = JSON.parse(ajax(lookup));
    if (doc.youtube.length === 0)
    {
        XML_Error("{{TEXT(PlexConnect)}}", "{{TEXT(TheMovieDB: No Trailer Info available)}}");
        return;
    }

    var id = doc.youtube[0].source;
    var url = "{{URL(/)}}&PlexConnect=PlayTrailer&PlexConnectTrailerID="+id
    atv.loadURL(url);
};



/*
 *  Small synchronous AJAX handler
 */
function ajax(url)
{
    var req = new XMLHttpRequest();
    req.open('GET', url, false);
    req.send();
    if(req.status == 200) return req.responseText;
}



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
    if (url.indexOf("{{URL()}}")!=-1)
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
    if (url.indexOf("{{URL()}}")!=-1)
    {
        url = url + "&PlexConnectUDID=" + atv.device.udid;
        url = url + "&PlexConnectATVName=" + encodeURIComponent(atv.device.displayName);
    }
    
    iOS_atv_loadAndSwapURL(url);
};