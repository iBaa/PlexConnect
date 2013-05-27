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

function checkSettings()
{
  var settings = atv.localStorage['PlexConnectSettings'];

  log("******************************************");
  log("Getting settings from atv")
  log("");
  if (!settings)
  {
    log("No settings found!");
    log("Creating default settings");
    
    settings = "PlexConnectSettings:MovieView:Grid:ShowView:List:SeasonView:List:ForceDirectPlay:false:ForceTranscode:false:TranscoderQuality:9"
    atv.localStorage['PlexConnectSettings'] = settings;
  }
  else 
  {
    settings = checkEachSetting(settings);
    atv.localStorage['PlexConnectSettings'] = settings;
  }
  
  log(settings);
  log("Sending settings to PlexConnect");
  loadPage("http://trailers.apple.com/&settings:" + atv.localStorage['PlexConnectSettings']);
  log("******************************************");
 //atv.localStorage['PlexConnectSettings'] = "PlexConnectSettings:MovieView:Grid:ShowView::ForceDirectPlay:false:ForceTranscode:false:TranscoderQuality:9";
};

function checkEachSetting(settings)
{
  newSettings = "PlexConnectSettings";
  newSettings = newSettings + ":" + getSetting("MovieView", "Grid", settings);
  newSettings = newSettings + ":" + getSetting("ShowView", "List", settings);
  newSettings = newSettings + ":" + getSetting("SeasonView", "List", settings);
  newSettings = newSettings + ":" + getSetting("ForceDirectPlay", "false", settings);
  newSettings = newSettings + ":" + getSetting("ForceTranscode", "false", settings);
  newSettings = newSettings + ":" + getSetting("TranscoderQuality", "false", settings);
  return newSettings;
}

function getSetting(name, deft, settings)
{
  var parts = settings.split(":");
  for (var i=0;i<parts.length;i++)
  {
    if (parts[i] == name) 
    {
      if (parts[i+1] == "")
      {
        log("adding: " + name + ":" + deft + "(default)");
        return name + ":" + deft;
      }
      else
      {
        log("Adding: " + name + ":" + parts[i+1]);
        return name + ":" + parts[i+1];
      }
    }
  }
  log("Adding: " + name + ":" + deft + "(default)");
  return name + ":" + deft;
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

atv.onAppEntry = function()
{
    checkSettings();
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
