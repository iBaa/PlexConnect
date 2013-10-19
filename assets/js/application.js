// settings for atv.player - communicated in PlayVideo/myMetadata
var addrPMS;
var ratingKey;
var duration;
var showClock, timeFormat, clockPosition, overscanAdjust;
var showEndtime;

// information for atv.player - computed internally to application.js
var lastReportedTime = -1;
var remainingTime = 0;


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
  * Handle ATV player time change
  */
atv.player.playerTimeDidChange = function(time)
{
  remainingTime = Math.round((parseInt(duration) / 1000) - time);
  thisReportTime = Math.round(time*1000);
  if (lastReportedTime == -1 || Math.abs(thisReportTime-lastReportedTime) > 5000)
  {
    lastReportedTime = thisReportTime;
    loadPage( addrPMS + '/:/timeline?ratingKey=' + ratingKey + 
                        '&duration=' + duration + 
                        '&key=%2Flibrary%2Fmetadata%2F' + ratingKey + 
                        '&state=playing' +
                        '&time=' + thisReportTime.toString() + 
                        '&X-Plex-Client-Identifier=' + atv.device.udid + 
                        '&X-Plex-Device-Name=' + encodeURIComponent(atv.device.displayName) );
// question: &key=... is the path correct? what about myplex? do we need it? send it down from PMS/PlexConnect?
  }
};

/*
 * Handle ATV playback stopped
 */
atv.player.didStopPlaying = function()
{	
  // Remove views
  if (clockTimer) atv.clearInterval(clockTimer);
  if (endTimer) atv.clearInterval(endTimer);
  Views = [];  
  
  // Notify of a stop.
  loadPage( addrPMS + '/:/timeline?ratingKey=' + ratingKey + 
                      '&duration=' + duration + 
                      '&key=%2Flibrary%2Fmetadata%2F' + ratingKey + 
                      '&state=stopped' +
                      '&time=' + lastReportedTime.toString() + 
                      '&X-Plex-Client-Identifier=' + atv.device.udid + 
                      '&X-Plex-Device-Name=' + encodeURIComponent(atv.device.displayName) );
    
  // Kill the session.
  loadPage(addrPMS + '/video/:/transcode/universal/stop?session=' + atv.device.udid);
};

/*
 * Handle ATV playback will start
 */
var assettimer = null;

atv.player.willStartPlaying = function()
{
  // mediaURL and myMetadata
  var url = atv.player.asset.getElementByTagName('mediaURL').textContent;
  var metadata = atv.player.asset.getElementByTagName('myMetadata');
  
  // get addrPMS, OSD settings, ...
  if (metadata != null)
  {
    addrPMS = metadata.getElementByTagName('addrPMS').textContent;
    ratingKey = metadata.getElementByTagName('ratingKey').textContent;
    duration = metadata.getElementByTagName('duration').textContent;
    showClock = metadata.getElementByTagName('showClock').textContent;
    timeFormat = metadata.getElementByTagName('timeFormat').textContent;
    clockPosition = metadata.getElementByTagName('clockPosition').textContent;
    overscanAdjust = metadata.getElementByTagName('overscanAdjust').textContent;
    showEndtime = metadata.getElementByTagName('showEndtime').textContent;
  }
  
  // Use loadMoreAssets callback for playlists - if not transcoding!
  if (metadata != null && url.indexOf('transcode/universal') == -1)
  {
    log('load assets')
    atv.player.loadMoreAssets = function(callback) 
    {
      assettimer = atv.setInterval(
        function()
        {
          atv.clearInterval(assettimer);
          
          var root = atv.player.asset;
          var videoAssets = root.getElementsByTagName('httpFileVideoAsset');
          if (videoAssets != null && videoAssets.length > 1)
            videoAssets.shift();
          else
            videoAssets = null;
          callback.success(videoAssets);
        } , 1000);
    }
  }
  
  // Create clock view
  containerView.frame = screenFrame;
  if (showClock == "True") initClockView();
  if (parseInt(duration) > 0 ) // TODO: grab video length from player not library????
  {
    if (showEndtime == "True") initEndTimeView();
  }
  // Paint the views on Screen.
  containerView.subviews = Views;
  atv.player.overlay = containerView;
  
  remainingTime = 0; // Reset remaining time
  
  log('willStartPlaying done');
};



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
 * Handle showing/hiding of transport controls
 */
atv.player.onTransportControlsDisplayed = function(animationDuration)
{
  var animation = {"type": "BasicAnimation", "keyPath": "opacity",
                    "fromValue": 0, "toValue": 1, "duration": animationDuration,
                    "removedOnCompletion": false, "fillMode": "forwards",
                    "animationDidStop": function(finished) {} };
  if (showClock == "True") containerView.addAnimation(animation, clockView)
  if (showEndtime == "True") containerView.addAnimation(animation, endTimeView)
};

atv.player.onTransportControlsHidden = function(animationDuration)
{
  var animation = {"type": "BasicAnimation", "keyPath": "opacity",
                    "fromValue": 1, "toValue": 0, "duration": animationDuration,
                    "removedOnCompletion": false, "fillMode": "forwards",
                    "animationDidStop": function(finished) {} };
  if (showClock == "True") containerView.addAnimation(animation, clockView)
  if (showEndtime == "True") containerView.addAnimation(animation, endTimeView)
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
    pingTimer = atv.setInterval(function() {loadPage( addrPMS + '/video/:/transcode/universal/ping?session=' + 
                                                                  atv.device.udid); }, 60000);
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
  loadPage( addrPMS + '/:/timeline?ratingKey=' + ratingKey + 
                      '&duration=' + duration + 
                      '&key=%2Flibrary%2Fmetadata%2F' + ratingKey + 
                      '&state=' + state + 
                      '&time=' + time.toString() + 
                      '&report=1' +
                      '&X-Plex-Client-Identifier=' + atv.device.udid + 
                      '&X-Plex-Device-Name=' + encodeURIComponent(atv.device.displayName) );
  }
};


/*
 *
 * Clock + End time rendering
 *
 */

var screenFrame = atv.device.screenFrame;
var containerView = new atv.View();
var Views = [];
var clockView;
var clockTimer;
var endTimeView;
var endTimer;

function pad(num, len) {return (Array(len).join("0") + num).slice(-len);};

function initClockView()
{
  clockView = new atv.TextView();
  var width = screenFrame.width * 0.15;
  if (timeFormat == '24 Hour')
  {
  width = screenFrame.width * 0.10;
  }
  var height = screenFrame.height * 0.06;
  var overscanadjust = 0.006 * (parseInt(overscanAdjust));
  var xmul = 0.1; //Default for Left Position
  if (clockPosition == 'Center') var xmul = 0.5;
  else if (clockPosition == 'Right') var xmul = 0.9;

  
  // Setup the clock frame
  clockView.backgroundColor = { red: 0, blue: 0, green: 0, alpha: 0.7};
  clockView.frame = { "x": screenFrame.x + (screenFrame.width * xmul) - (width * 0.5), 
                      "y": screenFrame.y + (screenFrame.height * (0.988 + overscanadjust)) - height,
                      "width": width, "height": height };

  // Update the overlay clock
  clockTimer = atv.setInterval( updateClock, 1000 );
  updateClock();
  
  // Add the view
  Views.push(clockView);
}

function initEndTimeView()
{
  endTimeView = new atv.TextView();
  var width = screenFrame.width * 0.10;
  if (timeFormat == '12 Hour')
  {
  width = screenFrame.width * 0.15;
  }
  var height = screenFrame.height * 0.03;
  var overscanadjust = 0.006 * (parseInt(overscanAdjust));
  var xmul = 0.1; // Default for Left Position
  if (clockPosition == 'Center') var xmul = 0.5;
  else if (clockPosition == 'Right') var xmul = 0.9;
    
  // Setup the end time frame
  endTimeView.backgroundColor = { red: 0, blue: 0, green: 0, alpha: 0.7};
  endTimeView.frame = { "x": screenFrame.x + (screenFrame.width * xmul) - (width * 0.5), 
                        "y": screenFrame.y + (screenFrame.height * (0.05 - overscanadjust)) - height,
                        "width": width, "height": height };

  // Update the overlay clock
  endTimer = atv.setInterval( updateEndTime, 1000 );
  updateEndTime();
  
  // Add the view
  Views.push(endTimeView);
}

function updateClock()
{
  var tail = "AM";
  var time = new Date();
  var hours24 = pad(time.getHours(), 2);
  var h12 = parseInt(hours24);
  if (h12 > 12) {h12 = h12 - 12; tail = "PM";}
  else if (h12 == 12) {tail = "PM";}
  else if (h12 == 0) {h12 = 12; tail = "AM";}
  hours12 = h12.toString();
  var mins = pad(time.getMinutes(), 2);
  var secs = pad(time.getSeconds(), 2);
  var timestr24 = hours24 + ":" + mins;
  var timestr12 = hours12 + ":" + mins + " " + tail;
  if (timeFormat == '24 Hour')
  {
    clockView.attributedString = {string: "" + timestr24,
      attributes: {pointSize: 36.0, color: {red: 1, blue: 1, green: 1}, alignment: "center"}};
  }
  else
  {
    clockView.attributedString = {string: "" + timestr12,
      attributes: {pointSize: 36.0, color: {red: 1, blue: 1, green: 1}, alignment: "center"}};
  }
};

function updateEndTime()
{
  var tail = "AM";
  var time = new Date();
  var intHours = parseInt(time.getHours());
  var intMins = parseInt(time.getMinutes());
  var intSecs = parseInt(time.getSeconds());
  var totalTimeInSecs = ((intHours * 3600) + (intMins * 60) + intSecs) + remainingTime;
  var endHours = Math.floor(totalTimeInSecs / 3600);
  if (endHours >= 24) { endHours = endHours - 24; }
  var endMins = Math.floor((totalTimeInSecs % 3600) / 60);
  var hours24 = pad(endHours.toString(), 2);
  var h12 = endHours;
  if (h12 > 12) { h12 = h12 - 12; tail = "PM"; }
  else if (h12 == 12) { tail = "PM"; }
  else if (h12 == 0) { h12 = 12; tail = "AM"; }
  hours12 = h12.toString();
  var mins = pad(endMins.toString(), 2);
  var timestr24 = hours24 + ":" + mins;
  var timestr12 = hours12 + ":" + mins + " " + tail;
  var endTimeStr = "Ends at:  "
  if (timeFormat == '24 Hour') { endTimeStr = endTimeStr + timestr24; }
  else { endTimeStr = endTimeStr + timestr12; }
  if (remainingTime == 0) { endTimeStr = ''; endTimeView.backgroundColor = { red: 0, blue: 0, green: 0, alpha: 0};}
  else { endTimeView.backgroundColor = { red: 0, blue: 0, green: 0, alpha: 0.7};}
  
  endTimeView.attributedString = {string: endTimeStr,
      attributes: {pointSize: 16.0, color: {red: 1, blue: 1, green: 1}, alignment: "center"}};
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
        atv.loadURL("http://atv.plexconnect/PlexConnect.xml&PlexConnectUDID=" + atv.device.udid);
    }
    else
    {
        var xmlstr =
'<?xml version="1.0" encoding="UTF-8"?> \
<atv> \
  <body> \
    <dialog id="com.sample.error-dialog"> \
      <title>{{TEXT(PlexConnect)}}</title> \
      <description>{{TEXT(ATV firmware version 5.1 or higher required. Please think about updating.)}}</description> \
    </dialog> \
  </body> \
</atv>';
        
        var doc = atv.parseXML(xmlstr);
        atv.loadXML(doc);
    }
};
