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



def XML_PMS2aTV(address, path):

    cmd = ''
    pos = string.find(path, "&PlexConnect=")
    if pos>-1:
        cmd = path[pos+len("&PlexConnect="):]
        path = path[:pos]
    
    PMS = XML_ReadFromURL(address, path)
    PMSroot = PMS.getroot()
    
    dprint(__name__, 1, PMSroot.get('viewGroup','None'))
    
    if cmd=='Play':
        XMLtemplate = 'PlayVideo.xml'
        path = path[:-len('&PlexConnect=Play')]
    
    elif cmd=='MoviePrePlay':
        XMLtemplate = 'MoviePrePlay.xml'
        path = path[:-len('&PlexConnect=MoviePrePlay')]
        
    elif PMSroot.get('viewGroup') is None or \
       PMSroot.get('viewGroup')=='secondary':
        XMLtemplate = 'Directory.xml'
        
    elif PMSroot.get('viewGroup')=='show':
        # TV Show grid view
        XMLtemplate = 'Show.xml'
        
    elif PMSroot.get('viewGroup')=='season':
        # TV Season view
        XMLtemplate = 'Season.xml'
        
    elif PMSroot.get('viewGroup')=='movie':
        # Movie listing
        XMLtemplate = 'Movie.xml'
        
    elif PMSroot.get('viewGroup')=='episode':
        # TV Episode view
        XMLtemplate = 'Episode.xml'
    
    dprint(__name__, 1, XMLtemplate)
        
    aTVTree = etree.parse(curdir+'/assets/templates/'+XMLtemplate)
    aTVroot = aTVTree.getroot()
    XML_Expand(aTVroot, PMSroot, path)
    
    # todo: channels, photos...
 
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



def XML_processParams(params, src):
            parts = params.split(':',2)
            attrib = parts[0]
            default=''
            if len(parts)>1:
                default = parts[1]
            leftover=''
            if len(parts)>2:
                leftover = parts[2]
            
            # walk the path if neccessary
            el = src            
            while '/' in attrib and el!=None:
                parts = attrib.split('/',1)
                el = el.find(parts[0])
                attrib = parts[1]
            
            # check element and get attribute
            if el!=None and attrib in el.attrib:
                res = el.get(attrib)
            
            else:  # path/attribute not found
                res = default
                leftover = ''  # clear leftover to keep the default
            
            dprint(__name__, 2, "XML_processParams: {},{}", res, leftover)
            return [res,leftover]



def XML_processVAL(res, conv):
    # apply string conversion
    if conv!='':
        parts = conv.split('|')
        convlist = []
        for part in parts:
            convstr = part.split('=')
            convlist.append((convstr[0], convstr[1]))
        
        for part in reversed(sorted(convlist)):
            if res>=part[0]: break
        
        res = part[1]
        
    dprint(__name__, 2, "XML_processVAL: {}", res)
    return res



def XML_processEVAL(res, math):
    # apply math function - eval
    if math!='':
        try:
            x = eval(res)
            res = str(eval(math))
        except:
            dprint(__name__, 0, "XML_processEVAL: Error in {}", math)
    
    dprint(__name__, 2, "XML_processEVAL: {}", res)
    return res



def XML_processMEDIAPATH(params, src):
    # walk the path if neccessary
    tag = params
    el = src            
    while True:
        parts = tag.split('/',1)
        el = el.find(parts[0])
        if not '/' in tag or el==None:
            break
        tag = parts[1]
    
    # check "Media' element and get key
    if el!=None:
        if Settings.getForceDirectPlay()==True or \
           Settings.getForceTranscoding()==False and \
           el.get('container','') in ("mov", "mp4") and \
           el.get('videoCodec','') in ("mpeg4", "h264") and \
           el.get('audioCodec','') in ("aac", "ac3"):
            # native aTV media
            res = el.find('Part').get('key','')
        else:
            # try transcoding
            dprint(__name__, 0, "XML_processMEDIAPATH - transcoding not implemented!")
            res = ''  # transcoding
    else:
        dprint(__name__, 0, "XML_processMEDIAPATH - element not found: {}", params)
        res = ''  # not found?
    
    dprint(__name__, 2, "XML_processMEDIAPATH: {}", res)
    return res



def XML_ExpandLine(elem, src, path, line):
    while True:
        cmd_start = line.find('{{')
        cmd_end   = line.find('}}')
        if cmd_start==-1 or cmd_end==-1:
            break;
        
        cmd = line[cmd_start+2:cmd_end]
        if cmd.startswith('VAL(') and cmd.endswith(')'):
            res, leftover = XML_processParams(cmd[len('VAL('):-1], src)
            res = XML_processVAL(res, leftover)
        
        elif cmd.startswith('EVAL(') and cmd.endswith(')'):
            res, leftover = XML_processParams(cmd[len('EVAL('):-1], src)
            res = XML_processEVAL(res, leftover)
        
        elif cmd.startswith('ADDPATH(') and cmd.endswith(')'):
            res, leftover = XML_processParams(cmd[len('ADDPATH('):-1], src)
            res = Path_addPath(path, res)
        
        elif cmd.startswith('MEDIAPATH(') and cmd.endswith(')'):
            res = XML_processMEDIAPATH(cmd[len('MEDIAPATH('):-1], src)
            
        elif cmd=='ADDR_PMS':
            res = Addr_PMS
        
        else:
            dprint(__name__, 0, "XML_ExpandLine - unknown command: {}", cmd)
            res = "[["+cmd+"]]"  # unsupported.
        
        line = line[:cmd_start] + res + line[cmd_end+2:]
        dprint(__name__, 2, "XML_ExpandLine: {}", line)
    return line



def XML_ModifyNode(elem, child, src, path, line):
    cmd_start = line.find('{{')  # only one command in text/tail? otherwise: todo
    cmd_end   = line.find('}}')
    if cmd_start==-1 or cmd_end==-1:
        return line  # tree not touched, line unchanged
    
    cmd = line[cmd_start+2:cmd_end]
    if cmd.startswith('COPY(') and cmd.endswith(')'):
        cmd = cmd[len('COPY('):-1]
        child.text = line[:cmd_start] + line[cmd_end+2:]  # remove current cmd
        
        childToCopy = child
        elem.remove(child)
        # duplicate child and add to tree
        for elemSRC in src.findall(cmd):  # tag
            el = copy.deepcopy(childToCopy)
            XML_Expand(el, elemSRC, path)
            elem.append(el)
        line = None  # tree modified, nodes updated: do not update line
    
    elif cmd.startswith('CUT(') and cmd.endswith(')'):
        res, leftover = XML_processParams(cmd[len('CUT('):-1], src)
        if res:
            elem.remove(child)
            line = None  # tree modified, node removed: do not update line
        else:
            line = line[:cmd_start] + line[cmd_end+2:]  # tree not touched, but update line
    
    else:
        pass  # tree not touched, line unchanged
    
    dprint(__name__, 2, "XML_ModifyNode: -{}-", line)
    return line



def XML_Expand(elem, src, path):
    # unpack template 'COPY'/'CUT' command in children
    line = ''
    res = ''
    while True:
        if list(elem)==[]:  # no sub-elements, stop recursion
            break
        
        for child in elem:  # todo: crashes/gives endless loop if multiple {{COPY}} in one template
            line = child.text
            if line!=None:
                line = line.strip()
                res = XML_ModifyNode(elem, child, src, path, line)
                if res!=line:  # tree changed - restart from top
                    if res!=None:
                        child.text = res
                    break
            
            line = child.tail
            if line!=None:
                line = line.strip()
                res = XML_ModifyNode(elem, child, src, path, line)
                if res!=line:  # tree changed - restart from top
                    if res!=None:
                        child.tail = res
                    break
        
        if res==line:  # complete tree parsed with no change
            break
    
    # unpack template commands in elem.text
    line = elem.text
    if line!=None:
        elem.text = XML_ExpandLine(elem, src, path, line.strip())
    
    # unpack template commands in elem.tail
    line = elem.tail
    if line!=None:
        elem.tail = XML_ExpandLine(elem, src, path, line.strip())
    
    # unpack template commands in elem.attrib.value
    for attrib in elem.attrib:
        line = elem.get(attrib)
        elem.set(attrib, XML_ExpandLine(elem, src, path, line.strip()))
 
    # recurse into children
    for el in elem:
        XML_Expand(el, src, path)



if __name__=="__main__":
    print "load PMS XML"
    _XML = '<PMS number="1" string="Hello"> \
                <DATA number="42" string="World"></DATA> \
                <DATA string="Moon"></DATA> \
            </PMS>'
    PMSroot = etree.fromstring(_XML)
    PMSTree = etree.ElementTree(PMSroot)
    XML_prettyprint(PMSTree)
    
    print
    print "load aTV XML template"
    _XML = '<aTV> \
                <INFO num="{{VAL(number)}}" str="{{VAL(string)}}">Info</INFO> \
                <FILE str="{{VAL(string)}}" strconv="{{VAL(string::World=big|Moon=small)}}" num="{{VAL(number:5)}}" numfunc="{{EVAL(number:5:int(x/10))}}"> \
                    File{{COPY(DATA)}}\
                </FILE> \
                <PATH path="{{ADDPATH(file:unknown)}}" /> \
                <accessories> \
                    <cut />{{CUT(number)}} \
                    <dontcut />{{CUT(attribnotfound)}} \
                </accessories> \
            </aTV>'
    aTVroot = etree.fromstring(_XML)
    aTVTree = etree.ElementTree(aTVroot)
    XML_prettyprint(aTVTree)
    
    print
    print "unpack PlexConnect commands"
    XML_Expand(aTVroot, PMSroot, '/library/sections/')
    
    print
    print "resulting aTV XML"
    XML_prettyprint(aTVTree)
    
    print
    #print "store aTV XML"
    #str = XML_prettystring(aTVTree)
    #f=open(curdir+'/XML/aTV_fromTmpl.xml', 'w')
    #f.write(str)
    #f.close()