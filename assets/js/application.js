// settings for atv.player - communicated in PlayVideo/myMetadata
var baseURL;
var accessToken;
var key;
var ratingKey;
var duration;
var showClock, timeFormat, clockPosition, overscanAdjust;
var showEndtime;
var subtitleURL, subtitleSize;


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
    var url = "{{URL(/)}}" + "&PlexConnectATVLogLevel=" + level.toString() + "&PlexConnectLog=" + encodeURIComponent(msg);
    req.open('GET', url, true);
    req.send();
};

 /*
  * Handle ATV player time change
  */
atv.player.playerTimeDidChange = function(time)
{
  remainingTime = Math.round((parseInt(duration) / 1000) - time);
  var thisReportTime = Math.round(time*1000)
  
  // correct thisReportTime with startTime if stacked media part
  if (atv.player.asset.getElementByTagName('startTime'))
    thisReportTime += parseInt(atv.player.asset.getElementByTagName('startTime').textContent)
  
  if (lastReportedTime == -1 || Math.abs(thisReportTime-lastReportedTime) > 5000)
  {
    lastReportedTime = thisReportTime;
    var token = '';
    if (accessToken!='')
        token = '&X-Plex-Token=' + accessToken;
    loadPage( baseURL + '/:/timeline?ratingKey=' + ratingKey + 
                        '&key=' + key +
                        '&duration=' + duration + 
                        '&state=playing' +
                        '&time=' + thisReportTime.toString() + 
                        '&X-Plex-Client-Identifier=' + atv.device.udid + 
                        '&X-Plex-Device-Name=' + encodeURIComponent(atv.device.displayName) +
                        token );
  }
  
  if (subtitle)
      updateSubtitle(thisReportTime);
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
  var token = '';
  if (accessToken!='')
      token = '&X-Plex-Token=' + accessToken;
  loadPage( baseURL + '/:/timeline?ratingKey=' + ratingKey + 
                      '&key=' + key +
                      '&duration=' + duration + 
                      '&state=stopped' +
                      '&time=' + lastReportedTime.toString() + 
                      '&X-Plex-Client-Identifier=' + atv.device.udid + 
                      '&X-Plex-Device-Name=' + encodeURIComponent(atv.device.displayName) +
                      token );
    
  // Kill the session.
  loadPage(baseURL + '/video/:/transcode/universal/stop?session=' + atv.device.udid);
};

/*
 * Handle ATV playback will start
 */
var assettimer = null;

atv.player.willStartPlaying = function()
{
    // getTextContent - return empty string if node not existing.
    function getTextContent(node)
    {
        if (node)
            return node.textContent;
        else
            return '';
    };
    
  // mediaURL and myMetadata
  var url = atv.player.asset.getElementByTagName('mediaURL').textContent;
  var metadata = atv.player.asset.getElementByTagName('myMetadata');
  
  // get baseURL, OSD settings, ...
  if (metadata != null)
  {
    baseURL = getTextContent(metadata.getElementByTagName('baseURL'));
    accessToken = getTextContent(metadata.getElementByTagName('accessToken'));
    
    key = getTextContent(metadata.getElementByTagName('key'));
    ratingKey = getTextContent(metadata.getElementByTagName('ratingKey'));
    duration = getTextContent(metadata.getElementByTagName('duration'));
    
    showClock = getTextContent(metadata.getElementByTagName('showClock'));
    timeFormat = getTextContent(metadata.getElementByTagName('timeFormat'));
    clockPosition = getTextContent(metadata.getElementByTagName('clockPosition'));
    overscanAdjust = getTextContent(metadata.getElementByTagName('overscanAdjust'));
    showEndtime = getTextContent(metadata.getElementByTagName('showEndtime'));
    
    subtitleURL = getTextContent(metadata.getElementByTagName('subtitleURL'));
    subtitleSize = getTextContent(metadata.getElementByTagName('subtitleSize'));
    log('willStartPlaying/getMetadata done');
  }
  
  // Use loadMoreAssets callback for playlists - if not transcoding!
  var stackedMedia = atv.player.asset.getElementByTagName('myStackedMedia');
  if (stackedMedia != null && url.indexOf('transcode/universal') == -1)
  {
      // determine startTime of stacked parts
      var startTime = 0;
      var videoAssets = stackedMedia.getElementsByTagName('httpFileVideoAsset');
      for (var i=0;i<videoAssets.length;i++)
      {
          if (videoAssets[i].getElementByTagName('startTime'))
              videoAssets[i].getElementByTagName('startTime').textContent = startTime.toString();
          startTime += parseInt(getTextContent(videoAssets[i].getElementByTagName('duration')));
      }
      //todo: work <bookmarkTime> and fix "resume" for stacked media
    
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
    log('willStartPlaying/loadMoreAssets done');
  }
  
  // load subtitle - aTV subtitle JSON
  subtitle = []
  subtitlePos = 0;
  // when... not transcoding or
  //         transcoding and PMS skips subtitle (dontBurnIn)
  if (subtitleURL &&
       ( url.indexOf('transcode/universal') == -1 ||
         url.indexOf('transcode/universal') > -1 && url.indexOf('skipSubtitles=1') > -1 )
     )
  {
    log("subtitleURL: "+subtitleURL);
    
    // read subtitle stream
    var req = new XMLHttpRequest();
    req.onreadystatechange = function()
    {
        if (req.readyState==4)  // 4: request is complete
        {
            subtitle = JSON.parse(req.responseText);
        }
    };
    req.open('GET', subtitleURL+"&PlexConnectUDID=" + atv.device.udid, true);  // true: asynchronous
    req.send();
    log('willStartPlaying/parseSubtitleJSON done');
  }
  
  var Views = [];
  
  // Create clock view
  containerView.frame = screenFrame;
  if (showClock == "True")
  {
      clockView = initClockView();
      Views.push(clockView);
  }
  if (parseInt(duration) > 0 ) // TODO: grab video length from player not library????
  {
    if (showEndtime == "True")
    {
        endTimeView = initEndTimeView();
        Views.push(endTimeView);
    }
  }
  log('willStartPlaying/createClockView done');
  
  // create subtitle view
  if (subtitleURL &&
       ( url.indexOf('transcode/universal') == -1 ||
         url.indexOf('transcode/universal') > -1 && url.indexOf('skipSubtitles=1') > -1 )
     )
  {
      subtitleView = initSubtitleView();
      for (var i=0;i<subtitleMaxLines;i++)
      {
          Views.push(subtitleView['shadowRB'][i]);
          Views.push(subtitleView['subtitle'][i]);
      }
      log('willStartPlaying/createSubtitleView done');
  }
  
  // Paint the views on Screen.
  containerView.subviews = Views;
  atv.player.overlay = containerView;
  //atv.player.overlay.subviews = Views;
  
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
  if (showClock == "True") clockView.addAnimation(animation, clockView)
  if (showEndtime == "True") endTimeView.addAnimation(animation, endTimeView)
};

atv.player.onTransportControlsHidden = function(animationDuration)
{
  var animation = {"type": "BasicAnimation", "keyPath": "opacity",
                    "fromValue": 1, "toValue": 0, "duration": animationDuration,
                    "removedOnCompletion": false, "fillMode": "forwards",
                    "animationDidStop": function(finished) {} };
  if (showClock == "True") clockView.addAnimation(animation, clockView)
  if (showEndtime == "True") endTimeView.addAnimation(animation, endTimeView)
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
    pingTimer = atv.setInterval(function() {loadPage( baseURL + '/video/:/transcode/universal/ping?session=' + 
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
  var thisReportTime = Math.round(timeIntervalSec*1000);
  
  // correct thisReportTime with startTime if stacked media part
  if (atv.player.asset.getElementByTagName('startTime'))
    thisReportTime += parseInt(atv.player.asset.getElementByTagName('startTime').textContent)
  
  var token = '';
  if (accessToken!='')
      token = '&X-Plex-Token=' + accessToken;
  loadPage( baseURL + '/:/timeline?ratingKey=' + ratingKey + 
                      '&key=' + key +
                      '&duration=' + duration + 
                      '&state=' + state + 
                      '&time=' + thisReportTime.toString() + 
                      '&report=1' +
                      '&X-Plex-Client-Identifier=' + atv.device.udid + 
                      '&X-Plex-Device-Name=' + encodeURIComponent(atv.device.displayName) +
                      token );
  }
};


/*
 *
 * Clock + End time rendering
 *
 */

var screenFrame = atv.device.screenFrame;
var containerView = new atv.View();
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
  
  return clockView;
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
  
  return endTimeView;
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
 * Subtitle handling/rendering
 *
 */
var subtitleView = {'shadowRB': [], 'subtitle': []};
var subtitle = [];
var subtitlePos = 0;
// constants
var subtitleMaxLines = 4;


function initSubtitleView()
{
  var width = screenFrame.width;
  var height = screenFrame.height * 1/14 * subtitleSize/100;  // line height: 1/14 seems to fit to 40pt font
  
  var xOffset = screenFrame.width * 1/640;  // offset for black letter shadow/border/background
  var yOffset = screenFrame.height * 1/360;
  
  // Setup the subtitle frames
  for (var i=0;i<subtitleMaxLines;i++)
  {
    // shadow right bottom
    subtitleView['shadowRB'][i] = new atv.TextView();
    subtitleView['shadowRB'][i].backgroundColor = { red: 0, blue: 0, green: 0, alpha: 0.0};
    subtitleView['shadowRB'][i].frame = { "x": screenFrame.x + xOffset,
                                          "y": screenFrame.y - yOffset + (height * (subtitleMaxLines-i-0.5)),
                                          "width": width, "height": height
                                        };
    // subtitle
    subtitleView['subtitle'][i] = new atv.TextView();
    subtitleView['subtitle'][i].backgroundColor = { red: 0, blue: 0, green: 0, alpha: 0.0};
    subtitleView['subtitle'][i].frame = { "x": screenFrame.x,
                                          "y": screenFrame.y + (height * (subtitleMaxLines-i-0.5)),
                                          "width": width, "height": height
                                        };
  }
  
  return subtitleView;
}


function updateSubtitle(time)
{
    // rewind, if needed
    while(subtitlePos>0 && time<subtitle.Timestamp[subtitlePos].time)
    {
        subtitlePos--;
    }
    // forward
    while(subtitlePos<subtitle.Timestamp.length-1 && time>subtitle.Timestamp[subtitlePos+1].time)
    {
        subtitlePos++;
    }
    // current subtitle to show: subtitle.Timestamp[subtitlePos]
    
    // get number of lines (max subtitleMaxLines)
    var lines
    if (subtitle.Timestamp[subtitlePos].Line)
        lines = Math.min(subtitle.Timestamp[subtitlePos].Line.length, subtitleMaxLines);
    else
        lines = 0;
    
    // update subtitleView[]
    var i_view=0;
    for (var i=0;i<subtitleMaxLines-lines;i++)  // fill empty lines on top
    {
        subtitleView['shadowRB'][i_view].attributedString = {
            string: "",
            attributes: { pointSize: 40.0 * subtitleSize/100,
                          color: {red: 0, blue: 0, green: 0, alpha: 1.0}
                        }
        };
        subtitleView['subtitle'][i_view].attributedString = {
            string: "",
            attributes: { pointSize: 40.0 * subtitleSize/100,
                          color: {red: 1, blue: 1, green: 1, alpha: 1.0}
                        }
        };
        i_view++;
    }
    for (var i=0;i<lines;i++)  // fill used lines
    {
        subtitleView['shadowRB'][i_view].attributedString = {
            string: subtitle.Timestamp[subtitlePos].Line[i].text,
            attributes: { pointSize: 40.0 * subtitleSize/100,
                          color: {red: 0, blue: 0, green: 0, alpha: 1.0},
                          weight: subtitle.Timestamp[subtitlePos].Line[i].weight || 'normal',
                          alignment: "center",
                          breakMode: "clip"
                        }
        };
        subtitleView['subtitle'][i_view].attributedString = {
            string: subtitle.Timestamp[subtitlePos].Line[i].text,
            attributes: { pointSize: 40.0 * subtitleSize/100,
                          color: {red: 1, blue: 1, green: 1, alpha: 1.0},
                          weight: subtitle.Timestamp[subtitlePos].Line[i].weight || 'normal',
                          alignment: "center",
                          breakMode: "clip"
                        }
        };
        i_view++;
    }
    
    if (time<10000)
        log("updateSubtitle done, subtitlePos="+subtitlePos);
}


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
        // discover - trigger PlexConnect, ignore response
        var url = "{{URL(/)}}&PlexConnect=Discover&PlexConnectUDID="+atv.device.udid
        var req = new XMLHttpRequest();
        req.open('GET', url, false);
        req.send();
        
        // load main page
        atv.loadURL("{{URL(/PlexConnect.xml)}}&PlexConnectUDID=" + atv.device.udid);
    }
    else
    {
        var xmlstr =
"<?xml version=\"1.0\" encoding=\"UTF-8\"?> \
<atv> \
  <body> \
    <dialog id=\"com.sample.error-dialog\"> \
      <title>{{TEXT(PlexConnect)}}</title> \
      <description>{{TEXT(ATV firmware version 5.1 or higher required. Please think about updating.)}}</description> \
    </dialog> \
  </body> \
</atv>";
        
        var doc = atv.parseXML(xmlstr);
        atv.loadXML(doc);
    }
};
