/*
 * lookup movie title, year, language on youtube and pass trailer ID to PlexConnect
 */
function playTrailer(title,year)
{
    var google_api_key = "putYoutOwnKey";
	var lookup = "https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=1&order=relevance&key="+google_api_key+"&q="+encodeURIComponent(title+" "+year+" trailer deutsch");

    var req = new XMLHttpRequest();
    req.open('GET', lookup, false);
    req.send();

    var doc = JSON.parse(req.responseText);

    if (doc.items[0].id.videoId.length === 0)
    {
        XML_Error("{{TEXT(PlexConnect)}}", "{{TEXT(Youtube: Kein Trailer gefunden)}}");
        return;
    }

    var id = doc.items[0].id.videoId;
    var url = "{{URL(/)}}&PlexConnect=PlayTrailer&PlexConnectTrailerID="+id;
    atv.loadURL(url);
};


/*
 * displays error message
 */
function XML_Error(title,desc)
{
    var errorXML =
"<?xml version=\"1.0\" encoding=\"UTF-8\"?> \
<atv> \
    <body> \
        <dialog id=\"com.sample.error-dialog\"> \
            <title>" + title + "</title> \
            <description>" + desc + "</description> \
        </dialog> \
    </body> \
</atv>";
    var doc = atv.parseXML(errorXML);
    atv.loadXML(doc); 
};
