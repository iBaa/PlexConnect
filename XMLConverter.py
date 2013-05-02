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

PlexAPI_getTranscodePath() based on getTranscodeURL from pyplex/plexAPI
https://github.com/megawubs/pyplex/blob/master/plexAPI/info.py
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

import time, uuid, hmac, hashlib, base64
from urllib import urlencode
from urlparse import urlparse

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
        if PMSroot.get('title2')=='On Deck':
            # TV On Deck View
            XMLtemplate = 'TV_OnDeck.xml'
        else:
            # TV Episode view
            XMLtemplate = 'Episode.xml'
    
    dprint(__name__, 1, XMLtemplate)
        
    aTVTree = etree.parse(curdir+'/assets/templates/'+XMLtemplate)
    aTVroot = aTVTree.getroot()
    XML_ExpandTree(aTVroot, PMSroot, path)
    XML_ExpandAllAttrib(aTVroot, PMSroot, path)
    
    # todo: channels, photos...
    
    dprint(__name__, 1, "====== generated aTV-XML ======")
    dprint(__name__, 1, XML_prettystring(aTVTree))
    dprint(__name__, 1, "====== aTV-XML finished ======")
    
    return etree.tostring(aTVroot)



def XML_ExpandTree(elem, src, path):
    # unpack template 'COPY'/'CUT' command in children
    res = False
    while True:
        if list(elem)==[]:  # no sub-elements, stop recursion
            break
        
        for child in elem:
            res = XML_ExpandNode(elem, child, src, path, 'TEXT')
            if res==True:  # tree modified: restart from 1st elem
                break  # "for child"
            
            res = XML_ExpandNode(elem, child, src, path, 'TAIL')
            if res==True:  # tree modified: restart from 1st elem
                break  # "for child"
        
        if res==False:  # complete tree parsed with no change, stop recursion
            break  # "while True"
    
    # recurse into children
    for el in elem:
        XML_ExpandTree(el, src, path)



def XML_ExpandNode(elem, child, src, path, text_tail):
    if text_tail=='TEXT':  # read line from text or tail
        line = child.text
    elif text_tail=='TAIL':
        line = child.tail
    else:
        dprint(__name__, 0, "XML_ExpandNode - text_tail badly specified: {}", text_tail)
        return False
        
    if line!=None:
        line = line.strip()
        cmd_start = line.find('{{')  # only one command in text/tail? otherwise: todo
        cmd_end   = line.find('}}')
        if cmd_start==-1 or cmd_end==-1:
            return False  # tree not touched, line unchanged
                
        cmd = line[cmd_start+2:cmd_end]
        if cmd[-1]!=')':
            dprint(__name__, 0, "XML_ExpandNode - closing bracket missing: {} ", line)
        
        parts = cmd.split('(',1)
        cmd = parts[0]
        param = parts[1].strip(')')  # remove ending bracket
        
        res = False
        if hasattr(CCommandTree, cmd):  # expand tree, work COPY, CUT
            if text_tail=='TEXT':  # remove cmd from text and tail
                child.text = line[:cmd_start] + line[cmd_end+2:]
            elif text_tail=='TAIL':
                child.tail = line[:cmd_start] + line[cmd_end+2:]
            CMD = CCommandTree(elem, child, path)
            try:
                res = eval("CMD."+cmd+"(src, '"+param+"')")
            except:
                dprint(__name__, 0, "XML_ExpandNode - Error in {}", line)
            del CMD
        
        dprint(__name__, 2, "XML_ExpandNode: {}", line)
        return res



def XML_ExpandAllAttrib(elem, src, path):
    # unpack template commands in elem.text
    line = elem.text
    if line!=None:
        elem.text = XML_ExpandLine(src, path, line.strip())
    
    # unpack template commands in elem.tail
    line = elem.tail
    if line!=None:
        elem.tail = XML_ExpandLine(src, path, line.strip())
    
    # unpack template commands in elem.attrib.value
    for attrib in elem.attrib:
        line = elem.get(attrib)
        elem.set(attrib, XML_ExpandLine(src, path, line.strip()))
    
    # recurse into children
    for el in elem:
        XML_ExpandAllAttrib(el, src, path)



def XML_ExpandLine(src, path, line):
    while True:
        cmd_start = line.find('{{')
        cmd_end   = line.find('}}')
        if cmd_start==-1 or cmd_end==-1:
            break;
        
        cmd = line[cmd_start+2:cmd_end]
        if cmd[-1]!=')':
            dprint(__name__, 0, "XML_ExpandLine - closing bracket missing: {} ", line)
        
        parts = cmd.split('(',1)
        cmd = parts[0]
        param = parts[1][:-1]  # remove ending bracket
        
        if hasattr(CCommandAttrib, cmd):  # expand tree, work VAL, EVAL...
            CMD = CCommandAttrib(path)
            try:                
                res = eval("CMD."+cmd+"(src, '"+param+"')")
                line = line[:cmd_start] + res + line[cmd_end+2:]
            except:
                dprint(__name__, 0, "XML_ExpandLine - Error in {}", line)
                line = line[:cmd_start] + "((ERROR:"+cmd+"))" + line[cmd_end+2:]
            del CMD
            
        dprint(__name__, 2, "XML_ExpandLine: {}", line)
    return line



"""
# PlexAPI
"""
def PlexAPI_getTranscodePath(path):
    transcodePath = '/video/:/transcode/segmented/start.m3u8?'
    
    args = dict()
    args['offset'] = 0
    args['3g'] = 0
    args['subtitleSize'] = 125
    args['secondsPerSegment'] = 10
    #args['ratingKey'] = ratingkey
    args["identifier"] = 'com.plexapp.plugins.library'
    args["quality"] = 9
    args["url"] = "http://" + Addr_PMS + path
    args["httpCookies"] = ''
    args["userAgent"] = ''
    
    atime = int(time.time())
    message = transcodePath + urlencode(args) + "@%d" % atime
    publicKey = 'KQMIY6GATPC63AIMC4R2'
    privateKey = base64.b64decode('k3U6GLkZOoNIoSgjDshPErvqMIFdE0xMTx8kgsrhnC0=')
    sig = base64.b64encode(hmac.new(privateKey, msg=message, digestmod=hashlib.sha256).digest())
    
    plexAccess = dict()
    plexAccess['X-Plex-Access-Key'] = publicKey
    plexAccess['X-Plex-Access-Time'] = atime
    plexAccess['X-Plex-Access-Code'] = sig
    plexAccess['X-Plex-Client-Capabilities'] = 'protocols=http-live-streaming,http-mp4-streaming,http-mp4-video,http-mp4-video-720p,http-streaming-video,http-streaming-video-720p;videoDecoders=h264{profile:main&resolution:720&level:42};audioDecoders=aac'
    
    dprint(__name__, 2, "TranscodePath: {}", transcodePath)
    dprint(__name__, 2, "Args: {}", urlencode(args))
    dprint(__name__, 2, "PlexAccess: {}", urlencode(plexAccess))
    return transcodePath + urlencode(args) + '&' + urlencode(plexAccess)



"""
# Command expander classes
# CCommandHelper(): base class to the following, provides basic parsing & evaluation functions
# CCommandTree():   commands with effect on the whole tree (COPY, CUT) - must be expanded first
# CCommandAttrib(): commands dealing with single node keys, text, tail only (VAL, EVAL, ADDR_PMS)
"""
class CCommandHelper():
    # internal helper functions
    def getParam(self, src, param):
        parts = param.split(':',1)
        param = parts[0]
        leftover=''
        if len(parts)>1:
            leftover = parts[1]
        
        param = param.replace('&col;',':')  # colon  # replace XML_template special chars
        param = param.replace('&ocb;','{')  # opening curly brace
        param = param.replace('&ccb;','}')  # closinging curly brace
        
        param = param.replace('&quot;','"')  # replace XML special chars
        param = param.replace('&apos;',"'")
        param = param.replace('&lt;','<')
        param = param.replace('&gt;','>')
        param = param.replace('&amp;','&')  # must be last
        
        dprint(__name__, 2, "CCmds_getParam: {}, {}", param, leftover)
        return [param, leftover]
    
    def getKey(self, src, param):
        attrib, leftover = self.getParam(src, param)
        default, leftover = self.getParam(src, leftover)
        
        # walk the path if neccessary
        el = src            
        while '/' in attrib and el!=None:
            parts = attrib.split('/',1)
            el = el.find(parts[0])
            attrib = parts[1]
        
        # check element and get attribute
        if el!=None and attrib in el.attrib:
            res = el.get(attrib)
            dfltd = False
        
        else:  # path/attribute not found
            res = default
            dfltd = True
        
        dprint(__name__, 2, "CCmds_getKey: {},{},{}", res, leftover,dfltd)
        return [res,leftover,dfltd]
    
    def getElement(self, src, param):
        tag, leftover = self.getParam(src, param)
        
        # walk the path if neccessary
        el = src
        while True:
            parts = tag.split('/',1)
            el = el.find(parts[0])
            if not '/' in tag or el==None:
                break
            tag = parts[1]
        return [el, leftover]
    
    def getConversion(self, src, param):
        conv, leftover = self.getParam(src, param)
        
        # build conversion "dictionary"
        convlist = []
        if conv!='':
            parts = conv.split('|',1)
            for part in parts:
                convstr = part.split('=')
                convlist.append((convstr[0], convstr[1]))
        
        dprint(__name__, 2, "CCmds_getConversion: {},{}", convlist, leftover)
        return [convlist, leftover]
    
    def applyConversion(self, val, convlist):
        # apply string conversion            
        if convlist!=[]:
            for part in reversed(sorted(convlist)):
                if val>=part[0]:
                    val = part[1]
                    break
        
        dprint(__name__, 2, "CCmds_applyConversion: {}", val)
        return val
    
    def applyMath(self, val, math, frmt):
        # apply math function - eval
        try:
            x = eval(val)
            if math!='':
                x = eval(math)
            val = ('{'+frmt+'}').format(x)
        except:
            dprint(__name__, 0, "CCmds_applyMath: Error in math {}, frmt {}", math, frmt)
        # apply format specifier
        
        dprint(__name__, 2, "CCmds_applyMath: {}", val)
        return val



class CCommandTree(CCommandHelper):
    def __init__(self, elem, child, path):
        self.elem = elem
        self.child = child
        self.path = path
    
    # XML tree modifier commands
    # add new commands to this list!
    def COPY(self, src, param):
        tag, leftover = self.getParam(src, param)
        childToCopy = self.child
        self.elem.remove(self.child)
        
        # duplicate child and add to tree
        for elemSRC in src.findall(tag):
            el = copy.deepcopy(childToCopy)
            XML_ExpandTree(el, elemSRC, self.path)
            XML_ExpandAllAttrib(el, elemSRC, self.path)
            self.elem.append(el)
                   
        return True  # tree modified, nodes updated: restart from 1st elem
    
    def CUT(self, src, param):
        key, leftover, dfltd = self.getKey(src, param)
        conv, leftover = self.getConversion(src, leftover)
        res = self.applyConversion(key, conv)
        if res:
            self.elem.remove(self.child)
            return True  # tree modified, node removed: restart from 1st elem
        else:
            return False  # tree unchanged



class CCommandAttrib(CCommandHelper):
    def __init__(self, path):
        self.path = path
    
    # XML line modifier commands
    # add new commands to this list!
    def VAL(self, src, param):
        key, leftover, dfltd = self.getKey(src, param)
        conv, leftover = self.getConversion(src, leftover)
        if not dfltd:
            key = self.applyConversion(key, conv)
        return key
    
    def EVAL(self, src, param):
        key, leftover, dfltd = self.getKey(src, param)
        math, leftover = self.getParam(src, leftover)
        frmt, leftover = self.getParam(src, leftover)
        if not dfltd:
            key = self.applyMath(key, math, frmt)
        return key
    
    def ADDPATH(self, src, param):
        addpath, leftover, dfltd = self.getKey(src, param)
        if addpath.startswith("/"):
            res = addpath+'/'
        else:
            res = self.path+addpath+'/'
        return res
    
    def MEDIAPATH(self, src, param):
        el, leftover = self.getElement(src,param)
        
        # check "Media" element and get key
        if el!=None:
            if Settings.getForceDirectPlay()==True or \
                Settings.getForceTranscoding()==False and \
                el.get('container','') in ("mov", "mp4") and \
                el.get('videoCodec','') in ("mpeg4", "h264") and \
                el.get('audioCodec','') in ("aac", "ac3"):
                # native aTV media
                res = el.find('Part').get('key','')
            else:
                # request transcoding
                res = el.find('Part').get('key','')
                res = PlexAPI_getTranscodePath(res)
        else:
            dprint(__name__, 0, "MEDIAPATH - element not found: {}", params)
            res = 'FILE_NOT_FOUND'  # not found?
        
        return res
    
    def ADDR_PMS(self, src, param):
        return Addr_PMS
        
    def episodestring(self, src, param):
        parentIndex, leftover, dfltd = self.getKey(src, param) # getKey "defaults" if nothing found.
        index, leftover, dfltd = self.getKey(src, leftover)
        title, leftover, dfltd = self.getKey(src, leftover)
        out = "{:0d}x{:02d} {}".format(int(parentIndex), int(index), title)
        return out 


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
                <FILE str="{{VAL(string)}}" strconv="{{VAL(string::World=big|Moon=small)}}" num="{{VAL(number:5)}}" numfunc="{{EVAL(number:5:int(x/10):&amp;col;02d)}}"> \
                    File{{COPY(DATA)}} \
                </FILE> \
                <PATH path="{{ADDPATH(file:unknown)}}" /> \
                <accessories> \
                    <cut />{{CUT(number::0=cut|1=)}} \
                    <dontcut />{{CUT(attribnotfound)}} \
                </accessories> \
                <ADDPATH>{{ADDPATH(string)}}</ADDPATH> \
                <ADDR_PMS>{{ADDR_PMS()}}</ADDR_PMS> \
                <COPY2>={{COPY(DATA)}}=</COPY2> \
            </aTV>'
    aTVroot = etree.fromstring(_XML)
    aTVTree = etree.ElementTree(aTVroot)
    XML_prettyprint(aTVTree)
    
    print
    print "unpack PlexConnect COPY/CUT commands"
    XML_ExpandTree(aTVroot, PMSroot, '/library/sections/')
    XML_ExpandAllAttrib(aTVroot, PMSroot, '/library/sections/')
    
    print
    print "resulting aTV XML"
    XML_prettyprint(aTVTree)
    
    print
    #print "store aTV XML"
    #str = XML_prettystring(aTVTree)
    #f=open(curdir+'/XML/aTV_fromTmpl.xml', 'w')
    #f.write(str)
    #f.close()