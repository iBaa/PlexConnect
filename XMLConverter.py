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



def XML_processParams(cmd, src):
            el = src
            param = string.strip(cmd, '()').split(':')
            func = param[0]
            name = param[1]
            
            while '/' in name:  # walk the path if neccessary
                param = name.split('/',1)
                el = el.find(param[0])
                name = param[1]
            
            dprint(__name__, 2, "XML_processParams: {},{},{}", func, el.tag, name)
            return [func, el, name]



def XML_ExpandLine(elem, src, path, line):
    while True:
        cmd_start = line.find('{{')
        cmd_end   = line.find('}}')
        if cmd_start==-1 or cmd_end==-1:
            break;
        
        cmd = line[cmd_start+2:cmd_end]
        if cmd.startswith('VAL('):
            func,el,name = XML_processParams(cmd[len('VAL('):], src)

            if func=='tag':  # todo
                res = ""
            elif func=='attrib':
                res = el.get(name,'')
            else:
                res = "{{"+cmd+"}}"  # unknown. keep it.
        
        elif cmd.startswith('ADDPATH('):
            func,el,name = XML_processParams(cmd[len('ADDPATH('):], src)
            
            if func=='tag':  # todo
                res = ""
            elif func=='attrib':
                res = Path_addPath(path, el.get(name,''))
            else:
                res = "{{"+cmd+"}}"  # unknown. keep it.
        
        elif cmd=='ADDR_PMS':
            res = Addr_PMS
        
        else:
            res = "{{"+cmd+"}}"  # unsupported.
        
        line = line[:cmd_start] + res + line[cmd_end+2:]
        dprint(__name__, 2, "XML_ExpandLine: {}", line)
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
                param = string.strip(cmd, '()').split(':')

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