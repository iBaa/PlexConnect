
/*
 * build Search/Refresh menu
 */
function sectionHoldSelect(id, searchKey, serverName, refreshKey, sectionName)
{
  log("sectionHoldSelect");

  var swVer = atv.device.softwareVersion.split(".");
  swVer = parseFloat(swVer[0] + "." + swVer[1]);
  if (swVer < 6.0)
  {
    // no popup menu, HoldSelect->Search only
    atv.loadURL(searchKey);
  }
  else
  {
    // popup menu, HoldSelect->Search/Refresh menu
    var xmlstr = " \
<atv> \
  <body> \
    <popUpMenu id='context_menu'> \
      <sections> \
        <menuSection> \
          <items> \
            <oneLineMenuItem id=\"item2\" onSelect=\"atv.loadURL('" + searchKey + "')\"> \
              <label>{{TEXT(Search)}} '" + serverName + "'</label> \
            </oneLineMenuItem> \
            <oneLineMenuItem id=\"item3\" onSelect=\"refreshSection('" + id + "', '" + refreshKey + "')\"> \
              <label>{{TEXT(Refresh)}} '" + sectionName + "'</label> \
            </oneLineMenuItem> \
          </items> \
        </menuSection> \
      </sections> \
    </popUpMenu> \
  </body> \
</atv> \
";
    var doc = atv.parseXML(xmlstr);
    atv.contextMenu.load(doc);
  }
}



/*
 * refresh section
 */
// todo: check for owned/shared
// today: shared servers shouldn't be triggered for refresh, should they?
var refreshSectionElem = [];
var refreshSectionTimer = [];

function refreshSection(id, refreshKey)
{
    setLabel = function(elem, label, text)
    {
        if (!elem.getElementByTagName(label))
        {
            elem_add = document.makeElementNamed(label);
            elem.appendChild(elem_add);
        }
        elem.getElementByTagName(label).textContent = text;
    };
    
    showPict = function(elem, pict)
    {
        var elem_add;
        if (!elem.getElementByTagName("accessories"))
        {
            elem_add = document.makeElementNamed("accessories");
            elem.appendChild(elem_add);
        }
        elem_add = document.makeElementNamed(pict);
        elem.getElementByTagName("accessories").appendChild(elem_add);
    };
    
    hidePict = function(elem, pict)
    {
        var elem_remove = elem.getElementByTagName("accessories").getElementByTagName(pict);
        if (!elem_remove) return undefined;  // error - element not found
        elem_remove.removeFromParent();
    };
    
    checkRefresh = function()
    {
        var timer = refreshSectionTimer.shift()
        var elem = refreshSectionElem.shift()
        
        // todo: check PMS XML for "refreshing=1", then stop timer and hide spinner
        // today: just reset spinner -> setTimeout() would be easier
        atv.clearInterval(timer);  // stop timer
        
        if (elem.tagName=='oneLineMenuItem' ||
            elem.tagName=='twoLineEnhancedMenuItem' )  // List
        {
            // reset spinner
            setLabel(elem, 'rightLabel', '');
            hidePict(elem, 'spinner');
        }
        else if (elem.tagName=='squarePoster')  // Grid, Bookcase
        {
            // reset subtitle
            setLabel(elem, 'subtitle', '');
        }
    };
    
    var elem = document.getElementById(id);
    if (!elem) return;  // error - element not found
    
    if (elem.tagName=='oneLineMenuItem' ||
        elem.tagName=='twoLineEnhancedMenuItem' )  // List
    {
        // add spinner
        setLabel(elem, 'rightLabel', "{{TEXT(refreshing)}}");
        showPict(elem, 'spinner');
    }
    else if (elem.tagName=='squarePoster')  // Grid, Bookcase
    {
        // add <refreshing>
        setLabel(elem, 'subtitle', "<{{TEXT(refreshing)}}>");
    }
    else
    {
        log('refreshSection() - unknown element '+elem.tagName);
    }
    
    // check status every 10sec
    refreshSectionElem.push(elem);
    refreshSectionTimer.push(atv.setInterval(checkRefresh, 10000));

    // request refresh
    var req = new XMLHttpRequest();
    req.open('PUT', refreshKey, false);
    req.send();
}
