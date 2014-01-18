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


// constants
var subtitleMaxLines = 4;


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
  thisReportTime = Math.round(time*1000);
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
  
  if (subtitleItem)
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
  // mediaURL and myMetadata
  var url = atv.player.asset.getElementByTagName('mediaURL').textContent;
  var metadata = atv.player.asset.getElementByTagName('myMetadata');
  
  // get baseURL, OSD settings, ...
  if (metadata != null)
  {
    // Todo: need exit strategy / defaulting if getElementByTagName doesn't return anything.
    baseURL = metadata.getElementByTagName('baseURL').textContent;
    accessToken = metadata.getElementByTagName('accessToken').textContent;
    
    key = metadata.getElementByTagName('key').textContent;
    ratingKey = metadata.getElementByTagName('ratingKey').textContent;
    duration = metadata.getElementByTagName('duration').textContent;
    
    showClock = metadata.getElementByTagName('showClock').textContent;
    timeFormat = metadata.getElementByTagName('timeFormat').textContent;
    clockPosition = metadata.getElementByTagName('clockPosition').textContent;
    overscanAdjust = metadata.getElementByTagName('overscanAdjust').textContent;
    showEndtime = metadata.getElementByTagName('showEndtime').textContent;
    
    subtitleURL = metadata.getElementByTagName('subtitleURL').textContent;
    subtitleSize = metadata.getElementByTagName('subtitleSize').textContent;
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
  
  // load subtitle - SRT only
  subtitleItem = [];
  subtitlePos = 0;
  // when... not transcoding or
  //         transcoding and PMS skips subtitle (dontBurnIn)
  if (subtitleURL &&
       ( url.indexOf('transcode/universal') == -1 ||
         url.indexOf('transcode/universal') > -1 && url.indexOf('skipSubtitles=\'1\'') > -1 )
     )
  {
    log("subtitleURL: "+subtitleURL);
    
    // read subtitle stream
    var req = new XMLHttpRequest();
    req.onreadystatechange = function()
    {
        if (req.readyState==4)  // 4: request is complete
        {
            parseSRT(req.responseText);
        }
    };
    req.open('GET', subtitleURL, false);  // true
    req.send();
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
  
  // create subtitle view
  log('create subtitleView');
  if (subtitleItem)
  {
      subtitleView = initSubtitleView();
      for (var i=0;i<subtitleMaxLines;i++)
          Views.push(subtitleView[i]);
  }
  log('create subtitleView done');
  
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
  time = Math.round(timeIntervalSec*1000);
  var token = '';
  if (accessToken!='')
      token = '&X-Plex-Token=' + accessToken;
  loadPage( baseURL + '/:/timeline?ratingKey=' + ratingKey + 
                      '&key=' + key +
                      '&duration=' + duration + 
                      '&state=' + state + 
                      '&time=' + time.toString() + 
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
var subtitleView = [];
var subtitleItem = [];
var subtitlePos = 0;

function initSubtitleView()
{
  var width = screenFrame.width;
  var height = screenFrame.height * 1/14 * subtitleSize/100;  // line height: 1/14 seems to fit to 40pt font
  
  // Setup the subtitle frames
  for (var i=0;i<subtitleMaxLines;i++)
  {
    subtitleView[i] = new atv.TextView();
    subtitleView[i].backgroundColor = { red: 0, blue: 0, green: 0, alpha: 0.0};
    subtitleView[i].frame = { "x": screenFrame.x,
                              "y": screenFrame.y + (height * (subtitleMaxLines-i-0.5)),
                              "width": width, "height": height
                            };
  }
  
  return subtitleView;
}


function updateSubtitle(time)
{
    // find currently active subtitleItem - forward
    // Todo: deal with rewind
    while(subtitlePos < subtitleItem.length && subtitleItem[subtitlePos]['timeHide']<time)
    {
        subtitlePos++;
    }
    
    // grab current subtitle
    var subtitle;
    if(subtitleItem[subtitlePos]['timeShow']<=time && time<=subtitleItem[subtitlePos]['timeHide'])
    {
        subtitle = subtitleItem[subtitlePos]['text'];
    }
    else
    {
        subtitle = ['','','',''];
    }
    
    // analyse format: <...> - i_talics (light), b_old (heavy), u_nderline (?), font color (Todo)
    // limitation (attributedString()): only one format per line/textView.
    var weight = [];
    for (var i=0;i<subtitleMaxLines;i++)
    {
        weight[i] = 'normal';
        if ((subtitleItem[subtitlePos]['format_i'])[i]) weight[i] = 'light';
        if ((subtitleItem[subtitlePos]['format_b'])[i]) weight[i] = 'heavy';
    }
    
    // update subtitleView[]
    for (var i=0;i<subtitleMaxLines;i++)
    {
        subtitleView[i].attributedString = {
            string: subtitle[i],
            attributes: { pointSize: 40.0 * subtitleSize/100,
                          color: {red: 1, blue: 1, green: 1, alpha: 1.0},
                          weight: weight[i],
                          alignment: "center"
                        }
        };
    }
}


function parseSRT(srtfile)
{
    subtitleItem = [];
    subtitlePos = 0;
    
    srtPart = srtfile.trim().split(/\r\n\r\n|\n\r\n\r|\n\n|\r\r/);  // trim whitespaces, split at double-newline
    for (var i=0;i<srtPart.length;i++)
    {
        var srtLine = srtPart[i].split(/\r\n|\n\r|\n|\r/);  // split at newline
        
        var timePart = srtLine[1].split(/:|,|-->/);  // <StartTime> --> <EndTime> split at : , or -->
        var timeShow = parseInt(timePart[0])*1000*60*60 +
                       parseInt(timePart[1])*1000*60 +
                       parseInt(timePart[2])*1000 +
                       parseInt(timePart[3]);
        var timeHide = parseInt(timePart[4])*1000*60*60 +
                       parseInt(timePart[5])*1000*60 +
                       parseInt(timePart[6])*1000 +
                       parseInt(timePart[7]);
        
        var lines = srtLine.length-2;
        if (lines>subtitleMaxLines)
            lines = subtitleMaxLines;
        
        var text = [];
        for(var j=0;j<subtitleMaxLines-lines;j++)  // fill empty lines on top
            text[j] = '';
        for(var j=0;j<lines;j++)  // fill subtitle to bottom lines
            text[j+subtitleMaxLines-lines] = srtLine[2+j];
        
        var format_i = [], format_i_next = false;
        var format_b = [], format_b_next = false;
        // analyse format: <...> - i_talics (ok), b_old (ok), u_nderline (?), font color (?)
        // Todo: carry over to next line...
        //       - current implementation too simple - what happens with mulitple <...>?
        // Todo: is there a way to add the format_x as a "property" to text[j]?
        for(var j=0;j<subtitleMaxLines;j++)
        {
            format_i[j] = format_i_next || (text[j].indexOf("<i>")!=-1);
            format_i_next = format_i[j] && !(text[j].indexOf("</i>")!=-1);
            format_b[j] = format_b_next || text[j].indexOf("<b>")!=-1;
            format_b_next = format_b[j] && !(text[j].indexOf("</b>")!=-1);
            
            text[j] = text[j].replace(/<.*?>/g, "");  // remove the formatting identifiers
        }
        
        subtitleItem.push({
            'ix':srtLine[0],
            'timeShow':timeShow, 'timeHide':timeHide,
            'lines':lines,
            'text':text,
            'format_i':format_i,
            'format_b':format_b
        });
    }
    log('parseSRT done');
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
