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
