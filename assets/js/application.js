var lastReportedTime = -1;
var addrPMS;

/*
 * Send http request
 */
function loadPage(url)
{
	var req = new XMLHttpRequest();
	req.open('GET', url, true);
	req.send();
};

 /*
  * ATVlogger
	*/
function log(msg)
{
    msg = msg.replace(/ /g, "%20")
    msg = msg.replace(/</g, "&lt;")
    msg = msg.replace(/>/g, "&gt;")
    msg = msg.replace(/\//g, "&fs;")
		msg = msg.replace(/"/g, "&qo;")
    
    loadPage("http://trailers.apple.com/" + msg + "&atvlogger");
};

 /*
  * Handle ATV player time change
	*/
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

/*
 * Handle ATV playback stopped
 */
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

/*
 * Handle ATV playback will start
 */
atv.player.willStartPlaying = function()
{	
    addrPMS = "http://" + atv.sessionStorage['addrpms'];
};

/*
 * Handle ATV player state changes
 */
 
var pingTimer = null;
 
atv.player.playerStateChanged = function(newState, timeIntervalSec) {
	log("Player state: " + newState + " at this time: " + timeIntervalSec);
	state = null;

	// Pause state, ping transcoder to keep session alive
	if (newState == 'Paused')
	{
	    state = 'paused';
		pingTimer = atv.setInterval(function() {loadPage(addrPMS + '/video/:/transcode/universal/ping?session=' + 
																											atv.device.udid);}, 60000);
	}

	// Playing state, kill paused state ping timer
	if (newState == 'Playing')
	{
	    state = 'play'
		atv.clearInterval(pingTimer);
	}

	// Loading state, tell PMS we're buffering
	if (newState == 'Loading')
	{
	    state = 'buffering';
	}

	if (state != null)
	{
    	time = Math.round(timeIntervalSec*1000);
    	loadPage(addrPMS + '/:/timeline?ratingKey=' + atv.sessionStorage['ratingKey'] + 
             '&duration=' + atv.sessionStorage['duration'] + 
             '&key=%2Flibrary%2Fmetadata%2F' + atv.sessionStorage['ratingKey'] + 
             '&state=' + state + 
             '&time=' + time.toString() + 
             '&report=1' +
             '&X-Plex-Client-Identifier=' + atv.device.udid + 
             '&X-Plex-Device-Name=Apple%20TV'
             );
    }
};

/*
 *
 * Main app entry point
 *
 */

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
        atv.loadURL("http://trailers.apple.com/versionError.xml");
    }
};
