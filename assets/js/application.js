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
    // Remove clock
    var messageTimer = TextViewController.getConfig("messageTimer");
    if (messageTimer)
    {  
        atv.clearInterval(messageTimer);
        TextViewController.setConfig("messageTimer", null);
    }
        
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
    // Create clock view
    if (atv.sessionStorage['showplayerclock'] != 'Off') TextViewController.initiateView("counter");
    
    addrPMS = "http://" + atv.sessionStorage['addrpms'];
};

/*
 * Handle showing/hiding of transport controls
 */
atv.player.onTransportControlsDisplayed = function(animationDuration)
{
    if (TextViewController.getView("counter"))
    {
        TextViewController.showView("counter", animationDuration);
    }
};

atv.player.onTransportControlsHidden = function(animationDuration)
{
    if (TextViewController.getView("counter"))
    {
        TextViewController.hideView("counter", animationDuration);
    }
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
 * Text view creation and animation
 *
 */

var TextViewController = (function() {
    var __config = {}, __views = {};
    
    function SetConfig(property, value)
    {
        if (property)
        {
            __config[property] = value;
        }
    };
    
    function GetConfig(property)
    {
        if (property)
        {
            return __config[property];
        } 
        else
        {
            return false;
        }
    };
    
    function SaveView(name, value)
    {
        if (name)
        {
            __views[name] = value;
        }
    };
    
    function GetView(name)
    {
        if (name)
        {
            return __views[name];
        }
        else
        {
            return false;
        }
    };
    
    function RemoveView(name)
    {
        if (GetView(name))
        {
            delete __views[name];
        }
    };
    
    function HideView(name, timeIntervalSec)
    {
        var animation = {"type": "BasicAnimation", "keyPath": "opacity",
                        "fromValue": 1, "toValue": 0, "duration": timeIntervalSec,
                        "removedOnCompletion": false, "fillMode": "forwards",
                        "animationDidStop": function(finished) {} };
        var viewContainer = GetView(name);
        if (viewContainer) viewContainer.addAnimation(animation, name);
    };
    
    function ShowView(name, timeIntervalSec)
    {
        var animation = {"type": "BasicAnimation", "keyPath": "opacity",
                        "fromValue": 0, "toValue": 1, "duration": timeIntervalSec,
                        "removedOnCompletion": false, "fillMode": "forwards",
                        "animationDidStop": function(finished) {} };
        var viewContainer = GetView( name );
        if (viewContainer) viewContainer.addAnimation(animation, name);
    };
    
    function pad(num, len) {return (Array(len).join("0") + num).slice(-len);};
    
    function __updateMessage()
    {
        var messageView = GetConfig("messageView");
        
        if(messageView)
        {
            var tail = "AM";
            var time = new Date();
            var hours24 = pad(time.getHours(), 2);
            var h12 = parseInt(hours24);
            if (h12 > 12)
            {
              h12 = h12 - 12;
              tail = "PM";
            }
            hours12 = h12.toString();
            var mins = pad(time.getMinutes(), 2);
            var secs = pad(time.getSeconds(), 2);
            var timestr24 = hours24 + ":" + mins + ":" + secs;
            var timestr12 = hours12 + ":" + mins + ":" + secs + " " + tail;
            if (atv.sessionStorage['showplayerclock'] == '24 Hour')
            {
                messageView.attributedString = {"string": "" + timestr24,
                                "attributes": {"pointSize": 30.0, "color": {"red": 1, "blue": 1, "green": 1}, "alignment": "center"}};
            }
            else
            {
                messageView.attributedString = {"string": "" + timestr12,
                                "attributes": {"pointSize": 30.0, "color": {"red": 1, "blue": 1, "green": 1}, "alignment": "center"}};
            }
        };
    };
    
    function InitiateView(name)
    {
        var viewContainer = new atv.View();
        var message = new atv.TextView();
        var screenFrame = atv.device.screenFrame;
        var width = screenFrame.width * 0.15;
        var height = screenFrame.height * 0.07;
                               
        // Setup the View container.
        viewContainer.frame = { "x": screenFrame.x + (screenFrame.width * 0.5) - (width * 0.5),
                                "y": screenFrame.y + (screenFrame.height * 0.993) - height,
                                "width": width, "height": height };
        viewContainer.backgroundColor = {"red": 0, "blue": 0, "green": 0, "alpha": 0.7};
        viewContainer.alpha = 1;
        
        var topPadding = viewContainer.frame.height * 0.15;
        
        // Setup the message frame
        message.frame = { "x": 0, "y": 0,
                          "width": viewContainer.frame.width, "height": viewContainer.frame.height - topPadding };

        // Update the overlay message
        var messageTimer = atv.setInterval( __updateMessage, 1000 );
        SetConfig("messageTimer", messageTimer)
        
          // Save the message to config
          SetConfig("messageView", message)
                          
        __updateMessage();
  
        // Add the sub view
        viewContainer.subviews = [message];
        
        // Paint the view on Screen.
        atv.player.overlay = viewContainer;
        SaveView( name, viewContainer );
    }
    
    return {
        "initiateView": InitiateView,
        "hideView": HideView,
        "showView": ShowView,
        "saveView": SaveView,
        "getView": GetView,
        "removeView": RemoveView,
        "setConfig": SetConfig,
        "getConfig": GetConfig
    }
} )();



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

