// Dependency: utils.js


getLabel = function(elem, label)
{
    var elem_label = elem.getElementByTagName(label);
    if (!elem_label) return undefined;  // error - element not found
    return(elem_label.textContent)
};

setLabel = function(elem, label, text)
{
    var elem_label = elem.getElementByTagName(label);
    if (elem_label) elem_label.textContent = text;
};

showPict = function(elem, pict)
{
    var elem_acc = elem.getElementByTagName("accessories");
    if (!elem_acc)
    {
        elem_acc = document.makeElementNamed("accessories");
        elem.appendChild(elem_acc);
    }
    var elem_add = document.makeElementNamed(pict);
    elem_acc.appendChild(elem_add);
};

hidePict = function(elem, pict)
{
    var elem_remove = elem.getElementByTagName("accessories");
    if (elem_remove) elem_remove = elem_remove.getElementByTagName(pict);
    if (elem_remove) elem_remove.removeFromParent();
};

doXMLHttpRequest = function(url, callback_ok, callback_nok)
{
    var req = new XMLHttpRequest();
    req.onreadystatechange = function()
    {
        try
        {
            if(req.readyState == 4)
            {
                callback_ok(req.responseXML);
            }
        }
        catch(e)
        {
            req.abort();
            callback_nok();
        }
    }
    req.open('GET', url, true);
    req.send();
}


/*
 * Plex Home - switch User
 */
switchHomeUser = function(id, prtct)
{
    var _failed = "{{TEXT(Failed)}}";
    
    var _id = id;
    var _pin = "";
    
    var _elem = document.getElementById(id);
    if (!_elem) return;  // error - element not found
    
    
    showPinEntryPage = function(in_title, in_prompt, in_initPinCode, callback_submit, callback_cancel)
    {
        log("switchHomeUser - showPinEntryPage");
        var pinEntry = new atv.PINEntry();
        
        pinEntry.title = in_title;
        pinEntry.prompt = in_prompt;
        pinEntry.initialPINCode = in_initPinCode;
        pinEntry.numDigits = 4;
        pinEntry.userEditable = true;
        pinEntry.hideDigits = false;
        pinEntry.onSubmit = callback_submit;
        pinEntry.onCancel = callback_cancel;
        
        pinEntry.show();
    };
    
    gotPin = function(value)
    {
        log("switchHomeUser - gotPin");
        _pin = value;
        doLogin();
    };
    
    gotCancel = function()
    {
        log("switchHomeUser - gotCancel");
        
        // sign out for defined status
        var url = "{{URL(/)}}" + 
                  "&PlexConnect=MyPlexLogoutHomeUser" +
                  "&PlexConnectUDID=" + atv.device.udid;
        doXMLHttpRequest(url, gotLogoutResponse, gotError);
    }
    
    gotLogoutResponse = function()
    {
        log("switchHomeUser - gotLogoutResponse");
        
        // discover - trigger PlexConnect, ignore response
        var url = "{{URL(/)}}&PlexConnect=Discover&PlexConnectUDID="+atv.device.udid;
        doXMLHttpRequest(url, gotDiscoverResponse, gotError);
    };
    
    // switch user - trigger PlexConnect, request updated settings page
    doLogin = function()
    {
        log("switchHomeUser - doLogin");
        var url = "{{URL(/PMS(plex.tv)/api/home/users)}}" + 
                  "&PlexConnect=MyPlexSwitchHomeUser" +
                  "&PlexConnectCredentials=" + encodeURIComponent(_id+':'+_pin) +
                  "&PlexConnectUDID=" + atv.device.udid;
        doXMLHttpRequest(url, gotLoginResponse, gotError);
    };
    
    // analyse updated page, update "paired"
    gotLoginResponse = function(doc)
    {
        log("switchHomeUser - gotLoginResponse");
        
        // update "paired" in place
        var new_elem = doc.getElementById(id);
        paired = new_elem.getElementsByTagName("paired");
        if (paired)
        {
            showPict(_elem, 'paired');
            log("switchHomeUser - login done");
        }
        else
        {
            setLabel(_elem, 'rightLabel', _failed);
            log("switchHomeUser - login failed");
        }
        
        // discover - trigger PlexConnect, ignore response
        var url = "{{URL(/)}}&PlexConnect=Discover&PlexConnectUDID="+atv.device.udid;
        doXMLHttpRequest(url, gotDiscoverResponse, gotError);
    };
    
    // done - clean up
    gotDiscoverResponse = function(doc)
    {
        log("switchHomeUser - gotDiscoverResponse");
        
        // done...
        hidePict(_elem, 'spinner');
    }
    
    // error - clean up
    gotError = function()
    {
        log("switchHomeUser - gotError");
        hidePict(_elem, 'spinner');
    }
    
    
    log("switchHomeUser");
    
    // remove "paired" from all users, remove label (eg. "failed")
    elem = document.getElementById('myPlexHomeUsers');
    elems = elem.getElementsByTagName('oneLineMenuItem');
    for (var i=0; i<elems.length; i++)
    {
        hidePict(elems[i], 'paired');
        setLabel(elems[i], 'rightLabel', '');
    }
    // show spinner on current item
    showPict(_elem, 'spinner');
    
    if (prtct=='1')
    {
        showPinEntryPage("{{TEXT(Plex Home User PIN)}}", "{{TEXT(PROMPT)}}", "0000", gotPin, gotCancel);
    }
    else
    {
        gotPin('');
    }
};


signOutHomeUser = function()
{
    var _elem = document.getElementById('signOutHomeUser');
    if (!_elem) return;  // error - element not found
    
    gotLogoutResponse = function(doc)
    {
        log("signOutHomeUser - gotLogoutResponse");
        
        // discover - trigger PlexConnect, ignore response
        var url = "{{URL(/)}}&PlexConnect=Discover&PlexConnectUDID="+atv.device.udid;
        doXMLHttpRequest(url, gotDiscoverResponse, gotError);
    };
    
    gotDiscoverResponse = function(doc)
    {
        log("signOutHomeUser - gotDiscoverResponse");
        hidePict(_elem, 'spinner');
    };
    
    // error - clean up
    gotError = function()
    {
        log("signOutHomeUser - gotError");
        hidePict(_elem, 'spinner');
    };
    
    
    log("signOutHomeUser");
    
    // remove "paired" from all users, remove label (eg. "failed")
    var elem = document.getElementById('myPlexHomeUsers');
    var elems = elem.getElementsByTagName('oneLineMenuItem');
    for (var i=0; i<elems.length; i++)
    {
        hidePict(elems[i], 'paired');
        setLabel(elems[i], 'rightLabel', '');
    }
    
    // show spinner on current item
    showPict(_elem, 'spinner');
    
    var url = "{{URL(/)}}" + 
              "&PlexConnect=MyPlexLogoutHomeUser" +
              "&PlexConnectUDID=" + atv.device.udid;
    doXMLHttpRequest(url, gotLogoutResponse, gotError);
};
