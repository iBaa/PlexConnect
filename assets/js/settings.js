// Dependency: utils.js


/*
 * update Settings
 */
function toggleSettings(opt, template) 
{
  // read new XML
  var url = "{{URL(/)}}&PlexConnect=SettingsToggle:"+ opt + "+" + template + "&PlexConnectUDID="+atv.device.udid
  var req = new XMLHttpRequest();
  req.open('GET', url, false);
  req.send();
  doc=req.responseXML;
  
  // get "opt" element of displayed XML
  var dispval = document.getElementById(opt).getElementByTagName("rightLabel");
  if (!dispval) // No rightlabel must be a checkmark :)
  {
    mainMenuItem = document.getElementById(opt);
    newMenuItem = doc.getElementById(opt);
    var mainAccessories = mainMenuItem.getElementByTagName("accessories");
    var newAccessories = newMenuItem.getElementByTagName("accessories");
    if ( mainAccessories ) mainAccessories.removeFromParent();
    if ( newAccessories )
    {
      accessories = document.makeElementNamed("accessories");
      var checkmark = document.makeElementNamed("checkMark");
      accessories.appendChild(checkmark);
      mainMenuItem.appendChild(accessories);
    }
    return;
  }

    // get "opt" element of fresh XML
  var newval = doc.getElementById(opt).getElementByTagName("rightLabel");
  if (!newval) return undefined;  // error - element not found
  
  log("new setting - "+opt+"="+newval.textContent);
    
  // push new value to display
  dispval.textContent = newval.textContent;
};

/*
 * discover
 */
function discover(opt, template) 
{
    gotDiscoverResponse = function(doc)
    {
        // request updated settings XML
        var url = "{{URL(/)}}&PlexConnect="+ template + "&PlexConnectUDID="+atv.device.udid
        var req = new XMLHttpRequest();
        req.open('GET', url, false);
        req.send();
        doc = req.responseXML;
        
        // get "opt" element of fresh XML
        var newval = doc.getElementById(opt).getElementByTagName("rightLabel");
        if (!newval) return undefined;  // error - element not found
        
        // push new value to display, remove spinner
        dispval.textContent = newval.textContent;
        var elem_remove = elem.getElementByTagName("accessories").getElementByTagName("spinner");
        if (elem_remove) elem_remove.removeFromParent();
        log("discover done - "+newval.textContent);
    }
    
  // get "opt" element of displayed XML
  var elem = document.getElementById(opt);
  if (!elem) return undefined;  // error - element not found
  var dispval = elem.getElementByTagName("rightLabel");
  if (!dispval) return undefined;  // error - element not found
  
  // clear number of PMSs, show spinner
  dispval.textContent =  '';
  if (!elem.getElementByTagName("accessories"))
  {
      var elem_add = document.makeElementNamed("accessories");
      elem.appendChild(elem_add);
  }
  var elem_add = document.makeElementNamed("spinner");
  elem.getElementByTagName("accessories").appendChild(elem_add);
  
  // discover - trigger PlexConnect, ignore response
  var url = "{{URL(/)}}&PlexConnect=Discover&PlexConnectUDID="+atv.device.udid
  var req = new XMLHttpRequest();
  req.onreadystatechange = function()
  {
        try
        {
            if(req.readyState == 4)
            {
                gotDiscoverResponse(req.responseXML)
            }
        }
        catch(e)
        {
            req.abort();
        }
  }
  req.open('GET', url, true);
  req.send();
};

/*
 * MyPlex sign in/out
 */

myPlexSignInOut = function()
{
    var _failed = "{{TEXT(Failed)}}"
    
    var _myPlexElem = document.getElementById('MyPlexSignInOut')
    if (!_myPlexElem) return;  // error - element not found
    
    
    getLabel = function(elem, label)
    {
        return(elem.getElementByTagName(label).textContent)
    }
    
    setLabel = function(elem, label, text)
    {
        elem.getElementByTagName(label).textContent = text;
    };
    
    showPict = function(elem, pict)
    {
        var elem_add = document.makeElementNamed(pict);
        elem.getElementByTagName("accessories").appendChild(elem_add);
    };
    
    hidePict = function(elem, pict)
    {
        var elem_remove = elem.getElementByTagName("accessories").getElementByTagName(pict);
        if (!elem_remove) return undefined;  // error - element not found
        elem_remove.removeFromParent();
    }; 
    
    // discover - trigger PlexConnect, ignore response
    reqDiscover = function()
    {
        var url = "{{URL(/)}}&PlexConnect=Discover&PlexConnectUDID="+atv.device.udid
        var req = new XMLHttpRequest();
        req.open('GET', url, false);
    req.send();
    };
    
    SignIn = function()
    {
        var _username = "";
        var _password = "";
        
        showTextEntryPage = function(input_type, input_title, input_instructions, callback_submit, callback_cancel, defaultvalue)
        {
            var textEntry = new atv.TextEntry();
            
            textEntry.type = input_type;
            textEntry.title = input_title;
            textEntry.instructions = input_instructions;
            textEntry.defaultValue = defaultvalue;
            textEntry.defaultToAppleID = false;
            //textEntry.image =
            textEntry.onSubmit = callback_submit;
            textEntry.onCancel = callback_cancel
           
            textEntry.show();
        };
        
        gotUsername = function(value)
        {
            _username = value;
            showTextEntryPage('password', "{{TEXT(MyPlex Password)}}", "{{TEXT(Enter the MyPlex password for {0}.)}}".format(_username), gotPassword, gotCancel, null);
        };
        
        gotPassword = function(value)
        {
            _password = value;
            doLogin();
        };
        
        gotCancel = function()
        {
            hidePict(_myPlexElem, 'spinner');
            showPict(_myPlexElem, 'arrow');
        };
        
        doLogin = function()
        {
            // login and get new settings page
            var url = "{{URL(/)}}" + 
                      "&PlexConnect=MyPlexLogin" +
                      "&PlexConnectCredentials=" + encodeURIComponent(_username+':'+_password) +
                      "&PlexConnectUDID=" + atv.device.udid
            var req = new XMLHttpRequest();
            req.open('GET', url, false);
            req.send();
            var doc = req.responseXML;
            var new_myPlexElem = doc.getElementById('MyPlexSignInOut')
            
            // update MyPlexSignInOut
            hidePict(_myPlexElem, 'spinner');
            setLabel(_myPlexElem, 'label', getLabel(new_myPlexElem, 'label'));
            var username = getLabel(new_myPlexElem, 'rightLabel')
            if (username)
            {
                setLabel(_myPlexElem, 'rightLabel', username);
                log("MyPlex Login - done");
                
                updateContextXML();  // open new page to "invalidate" this page/main navbar
            }
            else
            {
                showPict(_myPlexElem, 'arrow')
                setLabel(_myPlexElem, 'rightLabel', _failed);
                log("MyPlex Login - failed");
            }
        };
        
        setLabel(_myPlexElem, 'rightLabel', '');
        hidePict(_myPlexElem, 'arrow');
        showPict(_myPlexElem, 'spinner');
        showTextEntryPage('emailAddress', "{{TEXT(MyPlex Username)}}", "{{TEXT(To sign in to MyPlex, enter your Email address, username or Plex forum username.)}}", gotUsername, gotCancel, null);
    };
    
    
    SignOut = function()
    {
        doLogout = function()
        {
            atv.clearInterval(timer);
            
            // logout and get new settings page
            var url = "{{URL(/)}}" + 
                      "&PlexConnect=MyPlexLogout" +
                      "&PlexConnectUDID=" + atv.device.udid
            var req = new XMLHttpRequest();
            req.open('GET', url, false);
            req.send();
            var doc = req.responseXML;
            var new_myPlexElem = doc.getElementById('MyPlexSignInOut')
            
            // update MyPlexSignInOut
            hidePict(_myPlexElem, 'spinner');
            showPict(_myPlexElem, 'arrow');
            setLabel(_myPlexElem, 'label', getLabel(new_myPlexElem, 'label'));
            setLabel(_myPlexElem, 'rightLabel', getLabel(new_myPlexElem, 'rightLabel'));
            
            log("MyPlex Logout - done");
            
            updateContextXML();  // open new page to "invalidate" this page/main navbar
        };
        
        log("Signout");
        setLabel(_myPlexElem, 'rightLabel', '');
        hidePict(_myPlexElem, 'arrow');
        showPict(_myPlexElem, 'spinner');
        
        // timer: return control to iOS for a limited amount of time to activate spinner
        var timer = atv.setInterval(doLogout, 100);
    };
    
    
    var username = getLabel(_myPlexElem, 'rightLabel');
    
    if (username == '' ||
        username == _failed)
    {
        SignIn();
    }
    else
    {
        SignOut();
    }
    

};

/* 
 *  Save settings
 */
atv.onPageUnload = function(pageID) 
{
  if (pageID == 'SettingsPage')
  {
    var url = "{{URL(/)}}&PlexConnect=SaveSettings" 
    var req = new XMLHttpRequest();
    req.open('GET', url, false);
    req.send();
    log('Saving Settings file');
  }
}
