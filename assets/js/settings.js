// atv.Document extensions
if( atv.Document ) {
  atv.Document.prototype.getElementById = function(id) {
    var elements = this.evaluateXPath("//*[@id='" + id + "']", this);
    if ( elements && elements.length > 0 ) {
      return elements[0];
    }
    return undefined;
  }   
}

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

// string extension: format()
// see http://stackoverflow.com/a/4673436
if (!String.prototype.format) {
  String.prototype.format = function() {
    var args = arguments;
    return this.replace(/{(\d+)}/g, function(match, number) { 
      return typeof args[number] != 'undefined' ? args[number] : match;
    });
  };
}

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
  // get "opt" element of displayed XML
  var dispval = document.getElementById(opt).getElementByTagName("rightLabel");
  if (!dispval) return undefined;  // error - element not found
  
  // discover - trigger PlexConnect, ignore response
  var url = "{{URL(/)}}&PlexConnect=Discover&PlexConnectUDID="+atv.device.udid
  var req = new XMLHttpRequest();
  req.open('GET', url, false);
  req.send();
  
  // read new XML
  var url = "{{URL(/)}}&PlexConnect="+ template + "&PlexConnectUDID="+atv.device.udid
  var req = new XMLHttpRequest();
  req.open('GET', url, false);
  req.send();
  doc=req.responseXML;
  
  // get "opt" element of fresh XML
  var newval = doc.getElementById(opt).getElementByTagName("rightLabel");
  if (!newval) return undefined;  // error - element not found
  log("discover done - "+newval.textContent);
    
  // push new value to display
  dispval.textContent = newval.textContent;
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
            
            // discover
            discover('discover', 'Settings');
            
            // update MyPlexSignInOut
            hidePict(_myPlexElem, 'spinner');
            setLabel(_myPlexElem, 'label', getLabel(new_myPlexElem, 'label'));
            var username = getLabel(new_myPlexElem, 'rightLabel')
            if (username)
            {
                setLabel(_myPlexElem, 'rightLabel', username);
                atv.loadAndSwapURL("{{URL(/PlexConnect.xml)}}&PlexConnectUDID=" + atv.device.udid);
            }
            else
            {
                showPict(_myPlexElem, 'arrow')
                setLabel(_myPlexElem, 'rightLabel', _failed);
            }
            
            log("MyPlex Login - done");
        };
        
        setLabel(_myPlexElem, 'rightLabel', '');
        hidePict(_myPlexElem, 'arrow');
        showPict(_myPlexElem, 'spinner');
        showTextEntryPage('emailAddress', "{{TEXT(MyPlex Username)}}", "{{TEXT(To sign in to MyPlex, enter your Email address, username or Plex forum username.)}}", gotUsername, gotCancel, null);
    };
    
    
    SignOut = function()
    {
        // logout and get new settings page
        var url = "{{URL(/)}}" + 
                  "&PlexConnect=MyPlexLogout" +
                  "&PlexConnectUDID=" + atv.device.udid
        var req = new XMLHttpRequest();
        req.open('GET', url, false);
        req.send();
        var doc = req.responseXML;
        var new_myPlexElem = doc.getElementById('MyPlexSignInOut')
        
        // discover
        discover('discover', 'Settings');
        
        // update MyPlexSignInOut
        showPict(_myPlexElem, 'arrow');
        setLabel(_myPlexElem, 'label', getLabel(new_myPlexElem, 'label'));
        setLabel(_myPlexElem, 'rightLabel', getLabel(new_myPlexElem, 'rightLabel'));
        
        log("MyPlex Logout - done");
        
        atv.loadAndSwapURL("{{URL(/PlexConnect.xml)}}&PlexConnectUDID=" + atv.device.udid);
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
