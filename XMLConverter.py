#!/usr/bin/python

"""
Sources:

ElementTree
http://docs.python.org/2/library/xml.etree.elementtree.html#xml.etree.ElementTree.SubElement

trailers.apple.com root URL
http://trailers.apple.com/appletv/us/js/application.js
navigation pane
http://trailers.apple.com/appletv/us/nav.xml
->top trailers: http://trailers.apple.com/appletv/us/index.xml
->calendar:     http://trailers.apple.com/appletv/us/calendar.xml
->browse:       http://trailers.apple.com/appletv/us/browse.xml
"""


import sys
import inspect 
import string, cgi, time
from os import curdir, sep
import httplib, socket

try:
    import xml.etree.cElementTree as etree
except ImportError:
    import xml.etree.ElementTree as etree

import Settings



Addr_PMS = Settings.getIP_PMS()+':'+str(Settings.getPort_PMS())



"""
# XML in-place prettyprint formatter
# Source: http://stackoverflow.com/questions/749796/pretty-printing-xml-in-python
"""
def indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def XML_prettyprint(XML):
    indent(XML.getroot())
    XML.write(sys.stdout)



"""
# GetURL
# Source (somewhat): https://github.com/hippojay/plugin.video.plexbmc
"""
def GetURL(address, path):
    try:
        conn = httplib.HTTPConnection(Addr_PMS)
        conn.request("GET", path)
        data = conn.getresponse()
        if int(data.status) == 200:
            link=data.read()
            return link
        
        elif ( int(data.status) == 301 ) or ( int(data.status) == 302 ):
            return data.getheader('Location')
        
        elif int(data.status) >= 400:
            error = "HTTP response error: " + str(data.status) + " " + str(data.reason)
            print error
            return False
        
        else:      
            link=data.read()
            return link
    
    except socket.gaierror :
        error = 'Unable to lookup host: ' + Addr_PMS + "\nCheck host name is correct"
        print error
        return False
    except socket.error, msg : 
        error="Unable to connect to " + Addr_PMS +"\nReason: " + str(msg)
        print error
        return False



"""
# XML converter functions
# - get request from aTV
# - translate and send to PMS
# - receive reply from PMS
# - translate and feed back to aTV
"""
def XML_ReadFromURL(address, path):
    XMLstring = GetURL(address, path)
    
    # parse from memory
    XMLroot = etree.fromstring(XMLstring)    
    
    # XML root to ElementTree
    XML = etree.ElementTree(XMLroot)
    
    print("====== received XML-PMS ======")
    XML_prettyprint(XML)
    print("====== XML-PMS finished ======")
    
    return XML



def XML_Directory(elem, PMS_XML, path):
    PMSroot = PMS_XML.getroot()
    
    el = etree.SubElement(elem, "body")
    el = etree.SubElement(el, "listScrollerSplit", {'id':"com.sample.list-scroller-split"})
    ela = etree.SubElement(el, 'header')
    ela = etree.SubElement(ela, 'simpleHeader')
    ela = etree.SubElement(ela, 'title')
    if PMSroot.get('title1') is not None:
        ela.text = PMSroot.get('title1')
    else:
        ela.text = "Plex Connect"
    
    elb = etree.SubElement(el, 'menu') 
    elb = etree.SubElement(elb, 'sections')
    elb = etree.SubElement(elb, 'menuSection')
    
    elc = etree.SubElement(elb, 'header')
    elc = etree.SubElement(elc, 'textDivider', {'alignment':'left'})
    elc = etree.SubElement(elc, 'title')
    elc.text = "Selection:"
    
    eld = etree.SubElement(elb, 'items')
    # PMS Directories to headline
    PMS_dirs = PMSroot.findall('Directory')
    for i in PMS_dirs:
        key = i.get('key')
        if key.startswith("/"):
            el_path = 'http://trailers.apple.com'+key+'/'
        else:
            el_path = 'http://trailers.apple.com'+path+key+'/'
        
        el__ = etree.SubElement(eld, 'oneLineMenuItem', {'id':i.get('key')})
        el__.set('onSelect', "atv.loadURL('"+el_path+"')")
        el__.set('onPlay', "atv.loadURL('"+el_path+"')")
        
        el_Z = etree.SubElement(el__, 'label')
        el_Z.text = i.get('title')
        el_Z = etree.SubElement(el__, 'preview')
        el_Z = etree.SubElement(el_Z, 'link')
        el_Z.text = 'PREVIEW_URL'  # todo:



def XML_Movie(elem, PMS_XML, path):
    PMSroot = PMS_XML.getroot()
    
    el = etree.SubElement(elem, "body")
    el_scroller = etree.SubElement(el, "scroller", {'id':"com.sample.movie-grid"})
    ela = etree.SubElement(el_scroller, 'header')
    ela = etree.SubElement(ela, 'simpleHeader')
    ela = etree.SubElement(ela, 'title')
    ela.text = PMSroot.get('title1')
    
    el_items = etree.SubElement(el_scroller, "items")
    
    el_grid = etree.SubElement(el_items, "grid", {'id':"grid_0", 'columnCount':"7"})
    el_items2 = etree.SubElement(el_grid, "items")
    
    aTV_shelf_item = 1
    for i in PMSroot.findall('Video'):
        key = i.get('key')
        if key.startswith("/"):
            el_path = 'http://trailers.apple.com'+key+'/'
        else:
            el_path = 'http://trailers.apple.com'+path+key+'/'
        
        el_moviePoster=etree.SubElement(el_items2, "moviePoster")
        el_moviePoster.set('id', 'shelf_item_'+str(aTV_shelf_item))
        aTV_shelf_item += 1
        
        #el_moviePoster.set('accessibilityLabel', i.get('title'))
        #el_moviePoster.set('related', 'true')
        
        el_moviePoster.set('onSelect', "atv.loadURL('"+el_path+"&PlexConnect=Play')")  # todo: 'Select' - show metadata
        el_moviePoster.set('onPlay', "atv.loadURL('"+el_path+"&PlexConnect=Play')")
        el = etree.SubElement(el_moviePoster, 'title')
        el.text = i.get('title')
        el = etree.SubElement(el_moviePoster, 'subtitle')
        el.text = i.get('year')
        el = etree.SubElement(el_moviePoster, 'image')
        el.text = 'http://' + Addr_PMS + i.get('thumb')  # direct connect to Plex Media Server
        el = etree.SubElement(el_moviePoster, 'defaultImage')
        el.text = "resource://16X9.png"



def XML_Episode(elem, PMS_XML, path):
    PMSroot = PMS_XML.getroot()
    
    el = etree.SubElement(elem, "body")
    el_listWithPreview = etree.SubElement(el, "listWithPreview", {'id':"com.sample.menu-items-with-sections"})
    ela = etree.SubElement(el_listWithPreview, 'header')
    ela = etree.SubElement(ela, 'simpleHeader')
    elb = etree.SubElement(ela, 'title')
    elb.text = PMSroot.get('title1')
    elb = etree.SubElement(ela, 'subtitle')
    elb.text = PMSroot.get('title2')
    el_menu = etree.SubElement(el_listWithPreview, "menu")
    el_sections = etree.SubElement(el_menu, "sections")
    el_menuSection = etree.SubElement(el_sections, "menuSection")
    el_items = etree.SubElement(el_menuSection, "items")
    
    aTV_shelf_item = 1
    for i in PMSroot.findall('Video'):
        key = i.get('key')
        if key.startswith("/"):
            el_path = 'http://trailers.apple.com'+key+'/'
        else:
            el_path = 'http://trailers.apple.com'+path+key+'/'
        
        el_moviePoster=etree.SubElement(el_items, "twoLineEnhancedMenuItem")
        el_moviePoster.set('id', 'shelf_item_'+str(aTV_shelf_item))
        aTV_shelf_item += 1
        
        #el_moviePoster.set('accessibilityLabel', i.get('title'))
        #el_moviePoster.set('related', 'true')
        
        el_moviePoster.set('onSelect', "atv.loadURL('"+el_path+"&PlexConnect=Play')")  # todo: 'Select' - show metadata
        el_moviePoster.set('onPlay', "atv.loadURL('"+el_path+"&PlexConnect=Play')")
        
        el = etree.SubElement(el_moviePoster, 'label')
        el.text = i.get('title')
        el = etree.SubElement(el_moviePoster, 'ordinal')
        el.text = i.get('index')
        el = etree.SubElement(el_moviePoster, 'maxOrdinalDigits')
        el.text = '2'
        el = etree.SubElement(el_moviePoster, 'image')
        el.text = 'http://' + Addr_PMS + i.get('thumb')  # direct connect to Plex Media Server
        el = etree.SubElement(el_moviePoster, 'defaultImage')
        el.text = "resource://16X9.png"
        preview = etree.SubElement(el_moviePoster, 'preview')
        keyedPreview = etree.SubElement(preview, 'keyedPreview')
        kp = etree.SubElement(keyedPreview, 'title')
        kp.text = i.get('title')
        kp = etree.SubElement(keyedPreview, 'summary')
        kp.text = i.get('summary')
        kp = etree.SubElement(keyedPreview, 'image')
        kp.text = 'http://' + Addr_PMS + i.get('thumb')

def XML_TVSeason(elem, PMS_XML, path):
    PMSroot = PMS_XML.getroot()
    
    el = etree.SubElement(elem, "body")
    el_listWithPreview = etree.SubElement(el, "listWithPreview", {'id':"com.sample.menu-items-with-sections"})
    ela = etree.SubElement(el_listWithPreview, 'header')
    ela = etree.SubElement(ela, 'simpleHeader')
    elb = etree.SubElement(ela, 'title')
    elb.text = PMSroot.get('title2')

    el_menu = etree.SubElement(el_listWithPreview, "menu")
    el_sections = etree.SubElement(el_menu, "sections")
    el_menuSection = etree.SubElement(el_sections, "menuSection")
    el_items = etree.SubElement(el_menuSection, "items")
    
    aTV_shelf_item = 1
    for i in PMSroot.findall('Directory'):
        key = i.get('key')
        if key.startswith("/"):
            el_path = 'http://trailers.apple.com'+key+'/'
        else:
            el_path = 'http://trailers.apple.com'+path+key+'/'
        
        el_moviePoster=etree.SubElement(el_items, "oneLineMenuItem")
        el_moviePoster.set('id', 'shelf_item_'+str(aTV_shelf_item))
        aTV_shelf_item += 1
        
        #el_moviePoster.set('accessibilityLabel', i.get('title'))
        #el_moviePoster.set('related', 'true')
        
        el_moviePoster.set('onSelect', "atv.loadURL('"+el_path+"')")  # todo: 'Select' - show metadata
        el_moviePoster.set('onPlay', "atv.loadURL('"+el_path+"')")
        
        el = etree.SubElement(el_moviePoster, 'label')
        el.text = i.get('title')
        pv = etree.SubElement(el_moviePoster, "preview")
        cf = etree.SubElement(pv, "crossFadePreview")
        img = etree.SubElement(cf, 'image')
        img.text = 'http://' + Addr_PMS + i.get('thumb')  # direct connect to Plex Media Server
       
def XML_TVShow_ListView(elem, PMS_XML, path):
    PMSroot = PMS_XML.getroot()
    
    el = etree.SubElement(elem, "body")
    el_listWithPreview = etree.SubElement(el, "listWithPreview", {'id':"com.sample.menu-items-with-sections"})
    ela = etree.SubElement(el_listWithPreview, 'header')
    ela = etree.SubElement(ela, 'simpleHeader')
    elb = etree.SubElement(ela, 'title')
    elb.text = PMSroot.get('title2')

    el_menu = etree.SubElement(el_listWithPreview, "menu")
    el_sections = etree.SubElement(el_menu, "sections")
    el_menuSection = etree.SubElement(el_sections, "menuSection")
    el_items = etree.SubElement(el_menuSection, "items")
    
    aTV_shelf_item = 1
    for i in PMSroot.findall('Directory'):
        key = i.get('key')
        if key.startswith("/"):
            el_path = 'http://trailers.apple.com'+key+'/'
        else:
            el_path = 'http://trailers.apple.com'+path+key+'/'
        
        el_moviePoster=etree.SubElement(el_items, "oneLineMenuItem")
        el_moviePoster.set('id', 'shelf_item_'+str(aTV_shelf_item))
        aTV_shelf_item += 1
        
        #el_moviePoster.set('accessibilityLabel', i.get('title'))
        #el_moviePoster.set('related', 'true')
        
        el_moviePoster.set('onSelect', "atv.loadURL('"+el_path+"')")  # todo: 'Select' - show metadata
        el_moviePoster.set('onPlay', "atv.loadURL('"+el_path+"')")
        
        el = etree.SubElement(el_moviePoster, 'label')
        el.text = i.get('title')
        pv = etree.SubElement(el_moviePoster, "preview")
        cf = etree.SubElement(pv, "crossFadePreview")
        img = etree.SubElement(cf, 'image')
        img.text = 'http://' + Addr_PMS + i.get('thumb')  # direct connect to Plex Media Server
        
"""
<atv>
  <body>
    <videoPlayer id="com.sample.video-player">
      <httpFileVideoAsset id="[id]">
        <mediaURL>
          http://IP:Port/...[mp4/mov]
        </mediaURL>
        <title>Title</title>
        <description>
          Detailed Description
        </description>
        <image>
          http://IP:Port/...[jpg]
        </image>
      </httpFileVideoAsset>
    </videoPlayer>
  </body>
</atv>
"""
def XML_PlayVideo(address, path):
    PMS = XML_ReadFromURL(address, path)
    PMSroot = PMS.getroot()
    
    el_aTV = etree.Element("atv")
    el = etree.SubElement(el_aTV, "body")
    el = etree.SubElement(el, "videoPlayer", {'id':'com.sample.video-player'})
    el_file = etree.SubElement(el, "httpFileVideoAsset", {'id':PMSroot.find('Video').get('guid')})
    
    key = PMSroot.find('Video').find('Media').find('Part').get('key')  # todo: multipart video (->m3u8?)
    if key.startswith("/"):
        el_path = 'http://' + Addr_PMS + key
    else:
        el_path = 'http://' + Addr_PMS + path+key
    
    el = etree.SubElement(el_file, "mediaURL")
    el.text = el_path  # direct connect to Plex Media Server
    el = etree.SubElement(el_file, "title")
    el.text = PMSroot.find('Video').get('title')
    el = etree.SubElement(el_file, "description")
    el.text = PMSroot.find('Video').get('summary')
    el = etree.SubElement(el_file, "image")
    el.text = 'http://' + Addr_PMS + PMSroot.find('Video').get('art')
    
    aTVTree = etree.ElementTree(el_aTV)    
    
    print "====== generated aTV-XML (VIDEO) ======"
    XML_prettyprint(aTVTree)
    print "====== aTV-XML finished ======"
    
    return etree.tostring(el_aTV)



def XML_PMS2aTV(address, path):
    PMS = XML_ReadFromURL(address, path)
    PMSroot = PMS.getroot()
    
    el_aTV = etree.Element("atv")
    if PMSroot.get('viewGroup') is None or \
       PMSroot.get('viewGroup')=='secondary':
        XML_Directory(el_aTV, PMS, path)
       
    elif PMSroot.get('viewGroup')=='show':
        # TV Show grid view
        XML_TVShow_ListView(el_aTV, PMS, path)
        
    elif PMSroot.get('viewGroup')=='season':
        # TV season view
        XML_TVSeason(el_aTV, PMS, path)
        
    elif PMSroot.get('viewGroup')=='movie':
        # movie listing
        XML_Movie(el_aTV, PMS, path)
    
    elif PMSroot.get('viewGroup')=='episode':
        # TV episode view
        XML_Episode(el_aTV, PMS, path)
    
    # todo: channels, photos...
    
    aTVTree = etree.ElementTree(el_aTV)    
    
    print "====== generated aTV-XML ======"
    XML_prettyprint(aTVTree)
    print "====== aTV-XML finished ======"
    
    return etree.tostring(el_aTV)



if __name__=="__main__":
    # todo: Testcode: load PMS-XML from file, convert to aTV-XML
    # change the way XML_ReadFromURL() is used...
    pass