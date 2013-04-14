#!/usr/bin/python

"""
Sources:

ElementTree
http://docs.python.org/2/library/xml.etree.elementtree.html#xml.etree.ElementTree.SubElement

Webserver
http://fragments.turtlemeat.com/pythonwebserver.php
http://www.linuxjournal.com/content/tech-tip-really-simple-http-server-python
...stackoverflow.com and such

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
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import httplib, socket

try:
    import xml.etree.cElementTree as etree
except ImportError:
    import xml.etree.ElementTree as etree



IP_PMS = '192.168.178.20'  # Plex Media Server # todo: auto-discovery (Bonjour, GDM?)
Port_PMS = 32400

IP_client = '192.168.178.22'  # AppleTV # todo: how about more than one aTV?
#Port_client = 

aTV_address = 'http://trailers.apple.com'



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
        conn = httplib.HTTPConnection(IP_PMS+':'+str(Port_PMS))
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
        error = 'Unable to lookup host: ' + IP_PMS+':'+str(Port_PMS) + "\nCheck host name is correct"
        print error
        return False
    except socket.error, msg : 
        error="Unable to connect to " + IP_PMS+':'+str(Port_PMS) +"\nReason: " + str(msg)
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
    el_scroller = etree.SubElement(el, "scroller", {'id':"com.sample.movie-shelf"})
    ela = etree.SubElement(el_scroller, 'header')
    ela = etree.SubElement(ela, 'simpleHeader')
    ela = etree.SubElement(ela, 'title')
    ela.text = PMSroot.get('title1')
    
    el_items = etree.SubElement(el_scroller, "items")
    
    el_shelf = etree.SubElement(el_items, "shelf", {'id':"shelf_ID", 'columnCount':"5"})
    el_sections = etree.SubElement(el_shelf, "sections")
    el_shelfSection = etree.SubElement(el_sections, "shelfSection")
    el_items2 = etree.SubElement(el_shelfSection, "items")
    
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
        
        el = etree.SubElement(el_moviePoster, 'image')
        el.text = 'http://'+IP_PMS+':'+str(Port_PMS)+i.get('thumb')  # direct connect to Plex Media Server
        el = etree.SubElement(el_moviePoster, 'defaultImage')
        el.text = "resource://16X9.png"



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
        el_path = 'http://'+IP_PMS+':'+str(Port_PMS)+key
    else:
        el_path = 'http://'+IP_PMS+':'+str(Port_PMS)+path+key
    
    el = etree.SubElement(el_file, "mediaURL")
    el.text = el_path  # direct connect to Plex Media Server
    el = etree.SubElement(el_file, "title")
    el.text = PMSroot.find('Video').get('title')
    el = etree.SubElement(el_file, "description")
    el.text = PMSroot.find('Video').get('summary')
    el = etree.SubElement(el_file, "image")
    el.text = PMSroot.find('Video').get('art')
    
    aTVTree = etree.ElementTree(el_aTV)    
    
    print "====== generated aTV-XML (VIDEO) ======"
    XML_prettyprint(aTVTree)
    print "====== aTV-XML finished ======"
    
    return aTVTree



def XML_PMS2aTV(address, path):
    PMS = XML_ReadFromURL(address, path)
    PMSroot = PMS.getroot()
    
    aTV_address = 'http://trailers.apple.com'
    PMS_address = 'http://'+IP_PMS+':'+str(Port_PMS)
    
    el_aTV = etree.Element("atv")
    if PMSroot.get('viewGroup') is None or \
       PMSroot.get('viewGroup')=='secondary' or \
       PMSroot.get('viewGroup')=='show' or \
       PMSroot.get('viewGroup')=='season':
        # directory
        XML_Directory(el_aTV, PMS, path)
        
    elif PMSroot.get('viewGroup')=='movie' or \
         PMSroot.get('viewGroup')=='episode':
        # movie listing
        XML_Movie(el_aTV, PMS, path)
    
    # todo: channels, photos...
    
    aTVTree = etree.ElementTree(el_aTV)    
    
    print "====== generated aTV-XML ======"
    XML_prettyprint(aTVTree)
    print "====== aTV-XML finished ======"
    
    return aTVTree



class MyHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        try:
            if self.client_address[0]==IP_client:
                # serve "application.js" to aTV
                # disregard the path - it is different for different iOS versions
                if self.path.endswith("application.js"):
                    print "serving application.js"
                    f = open(curdir + sep + "assets" + sep + "application.js")
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(f.read())
                    f.close()
                    return
                
                # serve "plexconnect.xml" to aTV
                if self.path.endswith("plexconnect.xml"):
                    print "serving plexconnet.xml"
                    f = open(curdir + sep + "assets" + sep + "plexconnect.xml")
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(f.read())
                    f.close()
                    return
                
                # serve Plex directory structure - make sure to keep the trailing "/"                
                if self.path.endswith("/"):
                    print "serving .xml: "+self.path
                    XML = XML_PMS2aTV(self.client_address, self.path)
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(etree.tostring(XML.getroot()))
                    return
                
                # serve Plex media
                print self.headers
                if self.path.endswith("&PlexConnect=Play"):
                    print "serving media: "+self.path
                    XML = XML_PlayVideo(self.client_address, self.path[:-len('&PlexConnect=Play')])
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(etree.tostring(XML.getroot()))
                    return
                
                # unexpected request
                self.send_error(403,"Access denied: %s" % self.path)
            
            else:
                self.send_error(403,"Not Serving Client %s" % self.client_address[0])
        except IOError:
            self.send_error(404,"File Not Found: %s" % self.path)



if __name__=="__main__":
    #Protocol     = "HTTP/1.0"
    # todo: IP, port
    
    try:
        server = HTTPServer(('',80), MyHandler)
        
        sa = server.socket.getsockname()
        print "Serving HTTP on", sa[0], "port", sa[1], "..."
        server.serve_forever()
    except KeyboardInterrupt:
        print "^C received. Shutting down."
        server.socket.close()
