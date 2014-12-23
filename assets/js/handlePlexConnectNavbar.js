// Dependency: utils.js


// page internal storage
var navbarCurrentItemId = null;  // is there a clean way to grab unbuffered current index in reloadNavbar()?


/*
 * navigation bar - dynamic loading of menu pages
 */
function loadMenuPage(event)
{
    navbarCurrentItemId = event.navigationItemId;
    log("loadMenuPage: itemid="+navbarCurrentItemId);
    
    var item = document.getElementById(navbarCurrentItemId);
    var url = item.getElementByTagName('url').textContent;
    
    if (url.indexOf("{{URL(/)}}")!=-1)
    {
        url = url + "&PlexConnectUDID=" + atv.device.udid;
    }
    
    var req = new XMLHttpRequest();
    req.onreadystatechange = function()
    {
        try
        {
            if(req.readyState == 4)
            {
                doc = req.responseXML
                if(event) event.success(doc);
                else atv.loadXML(doc);
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
 * navigation bar - reload NavBar to update settings dependent items
 */
function reloadNavbar(event)
{
    log("reloadNavbar: itemid="+navbarCurrentItemId);
    
    if (navbarCurrentItemId == "Settings")
    {
        // "Settings" - reload Navbar content - stay at "Settings"
        var req = new XMLHttpRequest();
        req.onreadystatechange = function()
        {
            if(req.readyState == 4)
            {
                var doc = req.responseXML;
                
                var navItems = document.rootElement.getElementsByTagName('navigationItem');
                var rxNavItems = doc.rootElement.getElementsByTagName('navigationItem');
                
                // compare element count & content
                var changed = (navItems.length != rxNavItems.length);
                var i=0;
                while (!changed && i<navItems.length)
                {
                    changed = (navItems[i].getAttribute('id') != rxNavItems[i].getAttribute('id'));
                    i++;
                }
                
                if (!changed)
                {
                    // no change
                    log("reloadNavbar done: Settings unchanged - no action");
                    event.cancel();
                }
                else
                {
                    // reload, stay at Settings
                    // currentIndex -> Settings, which is last element
                    var navbar = doc.rootElement.getElementByTagName('navigation');
                    var currentIndex = (rxNavItems.length-1).toString();
                    navbar.setAttribute('currentIndex', currentIndex);
                    
                    log("reloadNavbar done: Settings changed - reload");
                    atv.loadAndSwapXML(doc);
                }
            }
        };
        
        var url = "{{URL(/PlexConnect.xml)}}" + "&PlexConnectUDID=" + atv.device.udid;
        req.open('GET', url, false);
        req.send();
    }
    else
    {
        // not at "Settings" - no change expected
        log("reloadNavbar done: itemId="+navbarCurrentItemId+" - no action");
        event.cancel();  // atv.loadAndSwapXML(document);
    }
};
