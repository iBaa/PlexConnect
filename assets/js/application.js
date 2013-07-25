var lastReportedTime = -1;
var addrPMS;
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
 * ATVlogger
 */
function log(msg)
{
  loadPage("http://trailers.apple.com/" + "&PlexConnectLog=" + encodeURIComponent(msg) );
};

 /*
  * Handle ATV player time change
  */
atv.player.playerTimeDidChange = function(time)
{
  remainingTime = Math.round((parseInt(atv.sessionStorage['duration']) / 1000) - time);
  thisReportTime = Math.round(time*1000);
  if (lastReportedTime == -1 || Math.abs(thisReportTime-lastReportedTime) > 5000)
  {
    lastReportedTime = thisReportTime;
    loadPage( addrPMS + '/:/timeline?ratingKey=' + atv.sessionStorage['ratingKey'] + 
                        '&duration=' + atv.sessionStorage['duration'] + 
                        '&key=%2Flibrary%2Fmetadata%2F' + atv.sessionStorage['ratingKey'] + 
                        '&state=playing' +
                        '&time=' + thisReportTime.toString() + 
                        '&X-Plex-Client-Identifier=' + atv.device.udid + 
                        '&X-Plex-Device-Name=' + encodeURIComponent(atv.device.displayName) );
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
  loadPage( addrPMS + '/:/timeline?ratingKey=' + atv.sessionStorage['ratingKey'] + 
                      '&duration=' + atv.sessionStorage['duration'] + 
                      '&key=%2Flibrary%2Fmetadata%2F' + atv.sessionStorage['ratingKey'] + 
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
atv.player.willStartPlaying = function()
{	
  // Create clock view
  containerView.frame = screenFrame;
  if (atv.sessionStorage['showplayerclock'] == "True") initClockView();
  if (parseInt(atv.sessionStorage['duration']) > 0 ) // TODO: grab video length from player not library????
  {
    if (atv.sessionStorage['showendtime'] == "True") initEndTimeView();
  }
  // Paint the views on Screen.
  containerView.subviews = Views;
  atv.player.overlay = containerView;
  
  addrPMS = "http://" + atv.sessionStorage['addrpms'];
};

/*
 * Handle showing/hiding of transport controls
 */
atv.player.onTransportControlsDisplayed = function(animationDuration)
{
  var animation = {"type": "BasicAnimation", "keyPath": "opacity",
                    "fromValue": 0, "toValue": 1, "duration": animationDuration,
                    "removedOnCompletion": false, "fillMode": "forwards",
                    "animationDidStop": function(finished) {} };
  if (atv.sessionStorage['showplayerclock'] == "True") containerView.addAnimation(animation, clockView)
  if (atv.sessionStorage['showendtime'] == "True") containerView.addAnimation(animation, endTimeView)
};

atv.player.onTransportControlsHidden = function(animationDuration)
{
  var animation = {"type": "BasicAnimation", "keyPath": "opacity",
                    "fromValue": 1, "toValue": 0, "duration": animationDuration,
                    "removedOnCompletion": false, "fillMode": "forwards",
                    "animationDidStop": function(finished) {} };
  if (atv.sessionStorage['showplayerclock'] == "True") containerView.addAnimation(animation, clockView)
  if (atv.sessionStorage['showendtime'] == "True") containerView.addAnimation(animation, endTimeView)
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
  loadPage( addrPMS + '/:/timeline?ratingKey=' + atv.sessionStorage['ratingKey'] + 
                      '&duration=' + atv.sessionStorage['duration'] + 
                      '&key=%2Flibrary%2Fmetadata%2F' + atv.sessionStorage['ratingKey'] + 
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
  var width = screenFrame.width * 0.10;
  if (atv.sessionStorage['timeformat'] == '12 Hour')
  {
  width = screenFrame.width * 0.15;
  }
  var height = screenFrame.height * 0.06;

  // Setup the clock frame
  clockView.backgroundColor = { red: 0, blue: 0, green: 0, alpha: 0.7};
  clockView.frame = { "x": screenFrame.x + (screenFrame.width * 0.5) - (width * 0.5), 
                      "y": screenFrame.y + (screenFrame.height * 0.988) - height,
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
  if (atv.sessionStorage['timeformat'] == '12 Hour')
  {
  width = screenFrame.width * 0.15;
  }
  var height = screenFrame.height * 0.03;

  // Setup the end time frame
  endTimeView.backgroundColor = { red: 0, blue: 0, green: 0, alpha: 0.7};
  endTimeView.frame = { "x": screenFrame.x + (screenFrame.width * 0.5) - (width * 0.5), 
                      "y": screenFrame.y + (screenFrame.height * 0.05) - height,
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
  if (atv.sessionStorage['timeformat'] == '24 Hour')
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
  if (atv.sessionStorage['timeformat'] == '24 Hour')
  {
    endTimeView.attributedString = {string: "Ends at:  " + timestr24,
      attributes: {pointSize: 16.0, color: {red: 1, blue: 1, green: 1}, alignment: "center"}};
  }
  else
  {
    endTimeView.attributedString = {string: "Ends at:  " + timestr12,
      attributes: {pointSize: 16.0, color: {red: 1, blue: 1, green: 1}, alignment: "center"}};
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

