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
import copy  # deepcopy()
from os import curdir, sep
import httplib, socket

try:
    import xml.etree.cElementTree as etree
except ImportError:
    import xml.etree.ElementTree as etree

import Settings
from Debug import *  # dprint()



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

def XML_prettystring(XML):
    indent(XML.getroot())
    return(etree.tostring(XML.getroot()))



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
            dprint(__name__, 0, error)
            return False
        
        else:      
            link=data.read()
            return link
    
    except socket.gaierror :
        error = "Unable to lookup host: " + Addr_PMS + "\nCheck host name is correct"
        dprint(__name__, 0, error)
        return False
    except socket.error, msg : 
        error = "Unable to connect to " + Addr_PMS + "\nReason: " + str(msg)
        dprint(__name__, 0, error)
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
    
    dprint(__name__, 1, "====== received XML-PMS ======")
    dprint(__name__, 1, XML_prettystring(XML))
    dprint(__name__, 1, "====== XML-PMS finished ======")
    
    return XML



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
    el.text = 'http://' + Addr_PMS + PMSroot.find('Video').get('thumb')
    
    aTVTree = etree.ElementTree(el_aTV)    
    
    dprint(__name__, 1, "====== generated aTV-XML (VIDEO) ======")
    dprint(__name__, 1, XML_prettystring(aTVTree))
    dprint(__name__, 1, "====== aTV-XML finished ======")
    
    return etree.tostring(el_aTV)



def XML_PMS2aTV(address, path):
    PMS = XML_ReadFromURL(address, path)
    PMSroot = PMS.getroot()
    
    #el_aTV = etree.Element("atv")
    if PMSroot.get('viewGroup') is None or \
       PMSroot.get('viewGroup')=='secondary':
        aTVTree = etree.parse(curdir+'/assets/templates/Directory.xml')
        aTVroot = aTVTree.getroot()
        XML_Expand(aTVroot, PMSroot, path)
        
    elif PMSroot.get('viewGroup')=='show':
        # TV Show grid view
        aTVTree = etree.parse(curdir+'/assets/templates/Show.xml')
        aTVroot = aTVTree.getroot()
        XML_Expand(aTVroot, PMSroot, path)
        
    elif PMSroot.get('viewGroup')=='season':
        # TV season view
        aTVTree = etree.parse(curdir+'/assets/templates/Season.xml')
        aTVroot = aTVTree.getroot()
        XML_Expand(aTVroot, PMSroot, path)
        
    elif PMSroot.get('viewGroup')=='movie':
        # movie listing
        aTVTree = etree.parse(curdir+'/assets/templates/Movie.xml')
        aTVroot = aTVTree.getroot()
        XML_Expand(aTVroot, PMSroot, path)
        
    elif PMSroot.get('viewGroup')=='episode':
        # TV episode view
        aTVTree = etree.parse(curdir+'/assets/templates/Episode.xml')
        aTVroot = aTVTree.getroot()
        XML_Expand(aTVroot, PMSroot, path)
    
    # todo: channels, photos...
    
    #aTVTree = etree.ElementTree(el_aTV)    
    
    dprint(__name__, 1, "====== generated aTV-XML ======")
    dprint(__name__, 1, XML_prettystring(aTVTree))
    dprint(__name__, 1, "====== aTV-XML finished ======")
    
    return etree.tostring(aTVroot)



def Path_addPath(path, addpath):
    if addpath.startswith("/"):
        res = addpath+'/'
    else:
        res = path+addpath+'/'
    return res



def XML_ExpandLine(elem, src, path, line):
    while True:
        cmd_start = line.find('{{')
        cmd_end   = line.find('}}')
        if cmd_start==-1 or cmd_end==-1:
            break;
        
        cmd = line[cmd_start+2:cmd_end]
        if cmd.startswith('VAL('):
            cmd = cmd[len('VAL('):]
            param = string.strip(cmd, '[]()').split(':')
            #print "VAL", param[0], param[1], line
            if param[0]=='tag':  # todo
                res = ""
            elif param[0]=='attrib':
                res = src.get(param[1],'')
        
        elif cmd.startswith('ADDPATH('):
            cmd = cmd[len('ADDPATH('):]
            param = string.strip(cmd, '[]()').split(':')
            #print "ADDPATH", param[0], param[1], line
            if param[0]=='tag':  # todo
                res = ""
            elif param[0]=='attrib':
                res = Path_addPath(path, src.get(param[1],''))
        
        elif cmd=='ADDR_PMS':
            res = Addr_PMS
    
        else:
            res = ""  # unsupported
        
        line = line[:cmd_start] + res + line[cmd_end+2:]
    
    return line



def XML_Expand(elem, src, path):

    # unpack template 'COPY' command in children
    for child in elem:
        line = child.text
        if line==None: line=''
        cmd_start = line.find('{{')
        cmd_end   = line.find('}}')    
        if cmd_start>-1 and cmd_end>-1:
            cmd = line[cmd_start+2:cmd_end]
            if cmd.startswith('COPY('):
                cmd = cmd[len('COPY('):]
                param = string.strip(cmd, '[]()').split(':')

                childToCopy = child
                elem.remove(child)
                childToCopy.text = line[:cmd_start] + line[cmd_end+2:]  # remove current cmd
                # duplicate child and add to tree                
                if param[0]=='tag':
                    for elemSRC in src.findall(param[1]):  # tag
                        el = copy.deepcopy(childToCopy)
                        XML_Expand(el, elemSRC, path)
                        elem.append(el)
                elif param[0]=='attrib':
                    pass  # todo
    
    # unpack template commands in elem.text
    line = elem.text
    if line==None: line=''
    elem.text = XML_ExpandLine(elem, src, path, line)
    
    # unpack template commands in elem.attrib.value
    for attrib in elem.attrib:
        line = elem.get(attrib)
        elem.set(attrib, XML_ExpandLine(elem, src, path, line))
 
    # recurse into children
    for el in elem:
        XML_Expand(el, src, path)



if __name__=="__main__":
    print "load PMS XML"    
    PMSTree = etree.parse(curdir+'/XML/PMS_Season.xml')
    PMSroot = PMSTree.getroot()
    #XML_prettyprint(PMStree)

    print "load aTV XML template"
    aTVTree = etree.parse(curdir+'/assets/templates/Season.xml')
    aTVroot = aTVTree.getroot()
    #XML_prettyprint(aTVtree)

    print "unpack PlexConnect commands"
    XML_Expand(aTVroot, PMSroot, '/library/sections/')
    #XML_prettyprint(aTVtree)

    print "store aTV XML"
    str = XML_prettystring(aTVTree)
    f=open(curdir+'/XML/aTV_fromTmpl.xml', 'w')
    f.write(str)
    f.close()