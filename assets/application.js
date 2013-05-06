var watchedPoint;
var watchedSet = false;
var resumePoint;
var addrPMS;

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
    while (intIndexOfMatch != -1){
        strReplaceAll = strReplaceAll.replace( " ", "%20" )
        intIndexOfMatch = strReplaceAll.indexOf( " " );
    }
    intIndexOfMatch = strReplaceAll.indexOf("<");
    while (intIndexOfMatch != -1){
        strReplaceAll = strReplaceAll.replace( "<", "&lt;" )
        intIndexOfMatch = strReplaceAll.indexOf( "<" );
    }
    intIndexOfMatch = strReplaceAll.indexOf(">");
    while (intIndexOfMatch != -1){
        strReplaceAll = strReplaceAll.replace( ">", "&gt;" )
        intIndexOfMatch = strReplaceAll.indexOf( ">" );
    }
    intIndexOfMatch = strReplaceAll.indexOf("/");
    while (intIndexOfMatch != -1){
        strReplaceAll = strReplaceAll.replace( "/", "&fs;" )
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
            loadPage(addrPMS + "/:/scrobble?key=" + atv.sessionStorage['ratingKey'] + "&identifier=com.plexapp.plugins.library"); // Set scrobble key for video
            loadPage(addrPMS + "/:/progress?key=" + atv.sessionStorage['ratingKey'] + "&identifier=com.plexapp.plugins.library&time=0"); // We've watched the file so set resume point to 0 seconds
            watchedSet = true;
        }
        else
        {
            resumePoint = Math.round(time*1000);
            loadPage(addrPMS + "/:/progress?key=" + atv.sessionStorage['ratingKey'] + "&identifier=com.plexapp.plugins.library&time=" + resumePoint.toString());
        }
    }
};

atv.player.willStartPlaying = function()
{	
        watchedPoint = parseInt(atv.sessionStorage['duration']); // Grab video duration from python server.
        watchedPoint = watchedPoint*0.00095; // Calculate the 95% time point in seconds.
        watchedSet = false;
        addrPMS = "http://" + atv.sessionStorage['addrpms'];
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
