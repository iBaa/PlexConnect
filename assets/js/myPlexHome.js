// Dependency: utils.js


getLabel = function(elem, label)
{
    var elem_label = elem.getElementByTagName(label);
    if (!elem_label) return '';  // error - element not found
    return(elem_label.textContent)
};

setLabel = function(elem, label, text)
{
    var elem_label = elem.getElementByTagName(label);
    if (!elem_label)
    {
        elem_label = document.makeElementNamed(label);
        elem.appendChild(elem_label);
    }
    elem_label.textContent = text;
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
        if (req.readyState == 4)
        {
            if (req.status == 200)
            {
                callback_ok(req.responseXML);
            }
            else
            {
                callback_nok();
            }
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
    var _switch = !_elem.getElementByTagName('paired');
    
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
        var url = "{{URL(/PMS(plex.tv)/api/home/users)}}" + 
                  "&PlexConnect=MyPlexLogoutHomeUser" +
                  "&PlexConnectUDID=" + atv.device.udid;
        doXMLHttpRequest(url, gotLoginResponse, gotError);
    }
    
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
    
    // analyse updated page, update "paired"  // evolved to Login/Logout response
    gotLoginResponse = function(doc)
    {
        log("switchHomeUser - gotLoginResponse");
        
        // update "paired" in place
        var new_elem = doc.getElementById(_id);
        setLabel(_elem, 'rightLabel', getLabel(new_elem, 'rightLabel'));
        var paired = new_elem.getElementByTagName('paired');
        if (_switch && paired)
        {
            showPict(_elem, 'paired');
            log("switchHomeUser - login done");
        }
        else if (_switch && !paired)
        {
            setLabel(_elem, 'rightLabel', _failed);
            log("switchHomeUser - login failed");
        }
        else
        {
            log("switchHomeUser - logout done");  // logout with response "paired" should never happen, obviously
        }
        
        hidePict(_elem, 'spinner');
    }
    
    // error - clean up
    gotError = function()
    {
        log("switchHomeUser - gotError");
        setLabel(_elem, 'rightLabel', _failed);
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
    
    if (_switch)
    {
        // switch home user
        if (prtct=='1')
        {
            var user = getLabel(_elem, 'label');
            showPinEntryPage("{{TEXT(PlexHome User PIN)}}", "{{TEXT(Enter the PlexHome user pin for {0}.)}}".format(user), "0000", gotPin, gotCancel);
        }
        else
        {
            gotPin('');
        }
    }
    else
    {
        // sign out home user
        var url = "{{URL(/PMS(plex.tv)/api/home/users)}}" + 
                  "&PlexConnect=MyPlexLogoutHomeUser" +
                  "&PlexConnectUDID=" + atv.device.udid;
        doXMLHttpRequest(url, gotLoginResponse, gotError);
    }
};
