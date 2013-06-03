var lastReportedTime = -1;
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
    msg = msg.replace(/ /g, "%20")
    msg = msg.replace(/</g, "&lt;")
    msg = msg.replace(/>/g, "&gt;")
    msg = msg.replace(/\//g, "&fs;")
    
    loadPage("http://trailers.apple.com/" + msg + "&atvlogger");
};

atv.player.playerTimeDidChange = function(time)
{
    thisReportTime = Math.round(time*1000);
    if (lastReportedTime == -1 || Math.abs(thisReportTime-lastReportedTime) > 5000)
    {
        lastReportedTime = thisReportTime;
        loadPage(addrPMS + '/:/timeline?ratingKey=' + atv.sessionStorage['ratingKey'] + 
                 '&duration=' + atv.sessionStorage['duration'] + 
                 '&key=%2Flibrary%2Fmetadata%2F' + atv.sessionStorage['ratingKey'] + 
                 '&state=playing' +
                 '&time=' + thisReportTime.toString() + 
                 '&X-Plex-Client-Identifier=' + atv.device.udid + 
                 '&X-Plex-Device-Name=Apple%20TV'
                 );
    }
};

atv.player.didStopPlaying = function()
{	
    // Notify of a stop.
    loadPage(addrPMS + '/:/timeline?ratingKey=' + atv.sessionStorage['ratingKey'] + 
             '&duration=' + atv.sessionStorage['duration'] + 
             '&key=%2Flibrary%2Fmetadata%2F' + atv.sessionStorage['ratingKey'] + 
             '&state=stopped' +
             '&time=' + lastReportedTime.toString() + 
             '&X-Plex-Client-Identifier=' + atv.device.udid + 
             '&X-Plex-Device-Name=Apple%20TV'
             );
    
    // Kill the session.
    loadPage(addrPMS + '/video/:/transcode/universal/stop?session=' + atv.device.udid);
};

atv.player.willStartPlaying = function()
{	
    addrPMS = "http://" + atv.sessionStorage['addrpms'];
};

atv.config = { 
    "doesJavaScriptLoadRoot": true,
    "DEBUG_LEVEL": 4
};

atv.player.playerStateChanged = function(newState, timeIntervalSec) {
	if (newState == 'Paused')
	{
		log("atv paused, pinging transcoded.");
		pingTimer = atv.setInterval(function() {loadPage(addrPMS + '/video/:/transcode/universal/ping?session=' + atv.device.udid);}, 60000);
	}
	
	if (newState == 'Playing')
	{
		log("atv playing.");
		atv.clearInterval(pingTimer);
	}
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
