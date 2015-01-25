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
    var elem_add = document.makeElementNamed(pict);
    elem.getElementByTagName("accessories").appendChild(elem_add);
};

hidePict = function(elem, pict)
{
    var elem_remove = elem.getElementByTagName("accessories");
    if (elem_remove) elem_remove = elem_remove.getElementByTagName(pict);
    if (elem_remove) elem_remove.removeFromParent();
};


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
    
    
    gotPin = function(value)
    {
        log("switchHomeUser - gotPin");
        _pin = value;
        doLogin();
    };
    
    // switch user - trigger PlexConnect, request updated settings page
    doLogin = function()
    {
        log("switchHomeUser - doLogin");
        var url = "{{URL(/PMS(plex.tv)/api/home/users)}}" + 
                  "&PlexConnect=MyPlexSwitchHomeUser" +
                  "&PlexConnectCredentials=" + encodeURIComponent(_id+':'+_pin) +
                  "&PlexConnectUDID=" + atv.device.udid
        var req = new XMLHttpRequest();
        req.onreadystatechange = function()
        {
            try
            {
                if(req.readyState == 4)
                {
                    gotLoginResponse(req.responseXML);
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
        var req = new XMLHttpRequest();
        req.onreadystatechange = function()
        {
            try
            {
                if(req.readyState == 4)
                {
                    gotDiscoverResponse(req.responseXML);
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
    
    // done - clean up
    gotDiscoverResponse = function(doc)
    {
        log("switchHomeUser - gotDiscoverResponse");
        
        // done...
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
    log("hidden");
    // show spinner on current item
    showPict(_elem, 'spinner');
    
    if (prtct=='1')
    {
        log("protected user");  // todo: request user input - 4 digit pin
    }
    else
    {
        gotPin('');
    }
};
