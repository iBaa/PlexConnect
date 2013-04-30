var watchedPoint;
var watchedSet = false;
var resumePoint;
var PMS = "http://192.168.0.200:32400";

function docToString(doc)
{
    parser=new DOMParser();
    xmlDoc=parser.parseFromString(xmlData,"text/xml");
    return xmlDoc;
};

function loadPage(url)
{
	var req = new XMLHttpRequest();
	req.open('GET', url, true);
	req.send();
};

function log(msg)
{
    var strReplaceAll = msg;
    var intIndexOfMatch = strReplaceAll.indexOf(" ");
    // Loop over the string value replacing out each matching substring.
    while (intIndexOfMatch != -1){
        // Relace out the current instance.
        strReplaceAll = strReplaceAll.replace( " ", "%20" )
        // Get the index of any next matching substring.
        intIndexOfMatch = strReplaceAll.indexOf( " " );
    }
    intIndexOfMatch = strReplaceAll.indexOf("<");
    // Loop over the string value replacing out each matching substring.
    while (intIndexOfMatch != -1){
        // Relace out the current instance.
        strReplaceAll = strReplaceAll.replace( "<", "&lt;" )
        // Get the index of any next matching substring.
        intIndexOfMatch = strReplaceAll.indexOf( "<" );
    }
    intIndexOfMatch = strReplaceAll.indexOf(">");
    // Loop over the string value replacing out each matching substring.
    while (intIndexOfMatch != -1){
        // Relace out the current instance.
        strReplaceAll = strReplaceAll.replace( ">", "&gt;" )
        // Get the index of any next matching substring.
        intIndexOfMatch = strReplaceAll.indexOf( ">" );
    }
    intIndexOfMatch = strReplaceAll.indexOf("/");
    // Loop over the string value replacing out each matching substring.
    while (intIndexOfMatch != -1){
        // Relace out the current instance.
        strReplaceAll = strReplaceAll.replace( "/", "&fs;" )
        // Get the index of any next matching substring.
        intIndexOfMatch = strReplaceAll.indexOf( "/" );
    }
    loadPage("http://trailers.apple.com/" + strReplaceAll + "&atvlogger");
};

atv.player.playerTimeDidChange = function(time)
{
    if (!watchedSet)
    {
        if (time>watchedPoint)
        {
            //atv.loadURL(PMS + "/:/scrobble?key=" + atv.sessionStorage['ratingKey'] + "&identifier=com.plexapp.plugins.library"); //Crap can't use atv.page loader
            loadPage(PMS + "/:/scrobble?key=" + atv.sessionStorage['ratingKey'] + "&identifier=com.plexapp.plugins.library"); // So we'll roll our own :)
            loadPage(PMS + "/:/progress?key=" + atv.sessionStorage['ratingKey'] + "&identifier=com.plexapp.plugins.library&time=0"); // We've watched the file so set resume point to 0 seconds
            log("Watched status set for ratingKey:" + atv.sessionStorage['ratingKey']);
            watchedSet = true;
        }
        else
        {
            resumePoint = Math.round(time*1000);
            loadPage(PMS + "/:/progress?key=" + atv.sessionStorage['ratingKey'] + "&identifier=com.plexapp.plugins.library&time=" + resumePoint.toString());
        }
    }
};

atv.player.willStartPlaying = function()
{	
        watchedPoint = parseInt(atv.sessionStorage['duration']); // Grab video duration from python server.
        watchedPoint = ((watchedPoint/100000)*95); // Calculate the 95% time point in seconds.
        watchedSet = false;
        
        
        log(docToString(document));
};

atv.config = { 
    "doesJavaScriptLoadRoot": true,
    "DEBUG_LEVEL": 4
};

atv.onAppEntry = function()
{
    fv = atv.device.softwareVersion.split(".");
    firmVer = fv[0] + "." + fv[1];
    if (parseFloat(firmVer) >= 5.1)
    {
        atv.loadURL("http://trailers.apple.com/plexconnect.xml");
    }
    else
    {
        atv.loadURL("http://trailers.apple.com/plexconnect_oldmenu.xml");
    }
};
