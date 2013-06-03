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
from os import sep
import httplib, socket

try:
    import xml.etree.cElementTree as etree
except ImportError:
    import xml.etree.ElementTree as etree

import time, uuid, hmac, hashlib, base64
from urllib import urlencode
from urlparse import urlparse
from urllib import quote_plus

import Settings, ATVSettings
from Debug import *  # dprint()



g_param = {}
def setParams(param):
    global g_param
    g_param = param

g_ATVSettings = None
def setATVSettings(cfg):
    global g_ATVSettings
    g_ATVSettings = cfg

UDID = '007'  # todo: aTV: send UDID, PlexConnect: grab UDID



# links to CMD class for module wide usage
g_CommandCollection = None



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
# aTV XML ErrorMessage - hardcoded XML File
"""
def XML_Error(title, desc):
    errorXML = '\
<?xml version="1.0" encoding="UTF-8"?>\n\
<atv>\n\
    <body>\n\
        <dialog id="com.sample.error-dialog">\n\
            <title>' + title + '</title>\n\
            <description>' + desc + '</description>\n\
        </dialog>\n\
    </body>\n\
</atv>\n\
';
    return errorXML



"""
# GetURL
# Source (somewhat): https://github.com/hippojay/plugin.video.plexbmc
"""
def GetURL(address, path):
    try:
        conn = httplib.HTTPConnection(g_param['Addr_PMS'], timeout=10)
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
        error = "Unable to lookup host: " + g_param['Addr_PMS'] + "\nCheck host name is correct"
        dprint(__name__, 0, error)
        return False
    except socket.error, msg : 
        error = "Unable to connect to " + g_param['Addr_PMS'] + "\nReason: " + str(msg)
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
    if XMLstring==False:
        dprint(__name__, 0, 'No Response from Plex Media Server')
        return False
    
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
    options = {}
    pos = string.find(path, "&PlexConnect=")
    if pos>-1:
        params = path[pos+1:].split('&')
        for p in params:
            param = p.split('=')
            options[param[0]] = param[1]
        cmd = options['PlexConnect']
        path = path[:pos]
        
    PMS = XML_ReadFromURL(address, path)
    if PMS==False:
        return XML_Error('PlexConnect', 'No Response from Plex Media Server')
    
    PMSroot = PMS.getroot()
    
    dprint(__name__, 1, PMSroot.get('viewGroup','None'))
    
    if cmd=='Play':
        XMLtemplate = 'PlayVideo.xml'
        
        Media = PMSroot.find('Video').find('Media')  # todo: needs to be more flexible?
        indirect = Media.get('indirect','0')
        Part = Media.find('Part')
        key = Part.get('key','')
        
        if indirect=='1':  # redirect... todo: select suitable resolution, today we just take first Media
            PMS = XML_ReadFromURL(address, key)  # todo... check key for trailing '/' or even 'http'
            PMSroot = PMS.getroot()

    elif cmd=='MoviePreview':
        XMLtemplate = 'MoviePreview.xml'
    
    elif cmd=='MoviePrePlay':
        XMLtemplate = 'MoviePrePlay.xml'
    
    elif cmd=='EpisodePrePlay':
        XMLtemplate = 'EpisodePrePlay.xml'
        
    elif cmd=='ChannelPrePlay':
        XMLtemplate = 'ChannelPrePlay.xml'
    
    elif cmd=='Channels':
        XMLtemplate = 'Channels.xml'
    
    elif cmd=='ChannelsVideo':
        XMLtemplate = 'ChannelsVideo.xml'
    
    elif cmd=='ByFolderPreview':
        XMLtemplate = 'ByFolderPreview.xml'
    
    elif cmd=='Search':
        XMLtemplate = 'Search_Results.xml'
    
    elif cmd=='Settings':
        XMLtemplate = 'Settings.xml'
    
    elif cmd.startswith('SettingsToggle:'):
        XMLtemplate = 'Settings.xml'
        
        opt = cmd[len('SettingsToggle:'):]  # cut command:
        g_ATVSettings.toggleSetting(UDID, opt.lower())
        dprint(__name__, 2, "ATVSettings->Toggle: {0}", opt)
        
    elif PMSroot.get('viewGroup') is None:
        XMLtemplate = 'Sections.xml'

    elif cmd == 'SectionPreview':
        XMLtemplate = 'SectionPreview.xml'

    elif PMSroot.get('viewGroup')=='secondary':
        XMLtemplate = 'Directory.xml'
        
    elif PMSroot.get('viewGroup')=='show':
        # TV Show grid view
        XMLtemplate = 'Show_'+g_ATVSettings.getSetting(UDID, 'showview')+'.xml'
        
    elif PMSroot.get('viewGroup')=='season':
        # TV Season view
        XMLtemplate = 'Season_'+g_ATVSettings.getSetting(UDID, 'seasonview')+'.xml'
        
    elif PMSroot.get('viewGroup')=='movie':
        if PMSroot.get('title2')=='By Folder':
          # By Folder View
          XMLtemplate = 'ByFolder.xml'
        else:
          # Movie listing
          XMLtemplate = 'Movie_'+g_ATVSettings.getSetting(UDID, 'movieview')+'.xml'
        
    elif PMSroot.get('viewGroup')=='episode':
        if PMSroot.get('title2')=='On Deck' or \
           PMSroot.get('title2')=='Recently Viewed Episodes' or \
           PMSroot.get('title2')=='Recently Aired' or \
           PMSroot.get('title2')=='Recently Added':
            # TV On Deck View
            XMLtemplate = 'TV_OnDeck.xml'
        else:
            # TV Episode view
            XMLtemplate = 'Episode.xml'
    
    elif PMSroot.get('viewGroup')=='photo':
        # Photo listing
        XMLtemplate = 'Photo.xml'
    
    dprint(__name__, 1, XMLtemplate)
        
    aTVTree = etree.parse(sys.path[0]+'/assets/templates/'+XMLtemplate)
    aTVroot = aTVTree.getroot()
    
    global g_CommandCollection
    g_CommandCollection = CCommandCollection(options, PMSroot, path)
    XML_ExpandTree(aTVroot, PMSroot, 'main')
    XML_ExpandAllAttrib(aTVroot, PMSroot, 'main')
    del g_CommandCollection
    
    # todo: channels, photos...
    
    dprint(__name__, 1, "====== generated aTV-XML ======")
    dprint(__name__, 1, XML_prettystring(aTVTree))
    dprint(__name__, 1, "====== aTV-XML finished ======")
  
    return etree.tostring(aTVroot)


def XML_ExpandTree(elem, src, srcXML):
    # unpack template 'COPY'/'CUT' command in children
    res = False
    while True:
        if list(elem)==[]:  # no sub-elements, stop recursion
            break
        
        for child in elem:
            res = XML_ExpandNode(elem, child, src, srcXML, 'TEXT')
            if res==True:  # tree modified: restart from 1st elem
                break  # "for child"
            
            res = XML_ExpandNode(elem, child, src, srcXML, 'TAIL')
            if res==True:  # tree modified: restart from 1st elem
                break  # "for child"
        
        if res==False:  # complete tree parsed with no change, stop recursion
            break  # "while True"
    
    # recurse into children
    for el in elem:
        XML_ExpandTree(el, src, srcXML)



def XML_ExpandNode(elem, child, src, srcXML, text_tail):
    if text_tail=='TEXT':  # read line from text or tail
        line = child.text
    elif text_tail=='TAIL':
        line = child.tail
    else:
        dprint(__name__, 0, "XML_ExpandNode - text_tail badly specified: {0}", text_tail)
        return False
    
    pos = 0
    while line!=None:
        cmd_start = line.find('{{',pos)
        cmd_end   = line.find('}}',pos)
        if cmd_start==-1 or cmd_end==-1 or cmd_start>cmd_end:
            return False  # tree not touched, line unchanged
        
        dprint(__name__, 2, "XML_ExpandNode: {0}", line)
        
        cmd = line[cmd_start+2:cmd_end]
        if cmd[-1]!=')':
            dprint(__name__, 0, "XML_ExpandNode - closing bracket missing: {0} ", line)
        
        parts = cmd.split('(',1)
        cmd = parts[0]
        param = parts[1].strip(')')  # remove ending bracket
        
        res = False
        if hasattr(CCommandCollection, 'TREE_'+cmd):  # expand tree, work COPY, CUT
            line = line[:cmd_start] + line[cmd_end+2:]  # remove cmd from text and tail
            if text_tail=='TEXT':  
                child.text = line
            elif text_tail=='TAIL':
                child.tail = line
            
            try:
                res = eval("g_CommandCollection.TREE_"+cmd+"(elem, child, src, srcXML, '"+param+"')")
            except:
                dprint(__name__, 0, "XML_ExpandNode - Error in cmd {0}, line {1}", cmd, line)
            
            if res==True:
                return True  # tree modified, node added/removed: restart from 1st elem
        
        elif hasattr(CCommandCollection, 'ATTRIB_'+cmd):  # check other known cmds: VAL, EVAL...
            dprint(__name__, 2, "XML_ExpandNode - Stumbled over {0} in line {1}", cmd, line)
            pos = cmd_end
        else:
            dprint(__name__, 0, "XML_ExpandNode - Found unknown cmd {0} in line {1}", cmd, line)
            line = line[:cmd_start] + "((UNKNOWN:"+cmd+"))" + line[cmd_end+2:]  # mark unknown cmd in text or tail
            if text_tail=='TEXT':
                child.text = line
            elif text_tail=='TAIL':
                child.tail = line
    
    dprint(__name__, 2, "XML_ExpandNode: {0} - done", line)
    return False



def XML_ExpandAllAttrib(elem, src, srcXML):
    # unpack template commands in elem.text
    line = elem.text
    if line!=None:
        elem.text = XML_ExpandLine(src, srcXML, line.strip())
    
    # unpack template commands in elem.tail
    line = elem.tail
    if line!=None:
        elem.tail = XML_ExpandLine(src, srcXML, line.strip())
    
    # unpack template commands in elem.attrib.value
    for attrib in elem.attrib:
        line = elem.get(attrib)
        elem.set(attrib, XML_ExpandLine(src, srcXML, line.strip()))
    
    # recurse into children
    for el in elem:
        XML_ExpandAllAttrib(el, src, srcXML)



def XML_ExpandLine(src, srcXML, line):
    pos = 0
    while True:
        cmd_start = line.find('{{',pos)
        cmd_end   = line.find('}}',pos)
        if cmd_start==-1 or cmd_end==-1 or cmd_start>cmd_end:
            break;
        
        dprint(__name__, 2, "XML_ExpandLine: {0}", line)
        
        cmd = line[cmd_start+2:cmd_end]
        if cmd[-1]!=')':
            dprint(__name__, 0, "XML_ExpandLine - closing bracket missing: {0} ", line)
        
        parts = cmd.split('(',1)
        cmd = parts[0]
        param = parts[1][:-1]  # remove ending bracket
        
        if hasattr(CCommandCollection, 'ATTRIB_'+cmd):  # expand line, work VAL, EVAL...
            
            try:
                res = eval("g_CommandCollection.ATTRIB_"+cmd+"(src, srcXML, '"+param+"')")
                line = line[:cmd_start] + res + line[cmd_end+2:]
                pos = cmd_start+len(res)
            except:
                dprint(__name__, 0, "XML_ExpandLine - Error in {0}", line)
                line = line[:cmd_start] + "((ERROR:"+cmd+"))" + line[cmd_end+2:]
        
        elif hasattr(CCommandCollection, 'TREE_'+cmd):  # check other known cmds: COPY, CUT
            dprint(__name__, 2, "XML_ExpandLine - stumbled over {0} in line {1}", cmd, line)
            pos = cmd_end
        else:
            dprint(__name__, 0, "XML_ExpandLine - Found unknown cmd {0} in line {1}", cmd, line)
            line = line[:cmd_start] + "((UNKNOWN:"+cmd+"))" + line[cmd_end+2:]    
        
        dprint(__name__, 2, "XML_ExpandLine: {0} - done", line)
    return line

"""
# PlexAPI
"""
def PlexAPI_getTranscodePath(options, path):
    transcodePath = '/video/:/transcode/universal/start.m3u8?'
    quality = { '1080p 12.0Mbps' :('1920x1080', '90', '12000'), \
                '480p 2.0Mbps' :('720x480', '60', '2000'), \
                '720p 3.0Mbps' :('1280x720', '75', '3000'), \
                '720p 4.0Mbps' :('1280x720', '100', '4000'), \
                '1080p 8.0Mbps' :('1920x1080', '60', '8000'), \
                '1080p 10.0Mbps' :('1920x1080', '75', '10000') }
    setQuality = g_ATVSettings.getSetting(UDID, 'transcodequality')
    vRes = quality[setQuality][0]
    vQ = quality[setQuality][1]
    mVB = quality[setQuality][2]
    dprint(__name__, 1, "Setting transcode quality Res:{0} Q:{1} {2}Mbps", vRes, vQ, mVB)
    dprint(__name__, 1, "Subtitle size: {0}", g_ATVSettings.getSetting(UDID, 'subtitlesize'))
    args = dict()
    args['protocol'] = 'hls'
    args['videoResolution'] = vRes # '1920x1080' # Base it on AppleTV model?
    args['directStream'] = '1'
    args['directPlay'] = '0'
    args['maxVideoBitrate'] = mVB # '12000'
    args['videoQuality'] = vQ # '90'
    args['subtitleSize'] = g_ATVSettings.getSetting(UDID, 'subtitlesize')
    args['audioBoost'] = '100'
    args['fastSeek'] = '1'
    args['path'] = path
    
    xargs = dict()
    xargs['X-Plex-Device'] = 'AppleTV'
    xargs['X-Plex-Version'] = ''
    xargs['X-Plex-Client-Platform'] = 'iOS'
    xargs['X-Plex-Device-Name'] = 'Apple TV'
    xargs['X-Plex-Model'] = '3,1' # Base it on AppleTV model.
    xargs['X-Plex-Platform'] = 'iOS'
    xargs['X-Plex-Product'] = 'Plex Connect'
    xargs['X-Plex-Platform-Version'] = '5.3' # Base it on AppleTV.
    
    if options.has_key('PlexUDID'):
        args['session'] = options['PlexUDID']
    
    return transcodePath + urlencode(args) + '&' + urlencode(xargs)

"""
# Command expander classes
# CCommandHelper(): base class to the following, provides basic parsing & evaluation functions
# CCommandTree():   commands with effect on the whole tree (COPY, CUT) - must be expanded first
# CCommandAttrib(): commands dealing with single node keys, text, tail only (VAL, EVAL, ADDR_PMS)
"""
class CCommandHelper():
    def __init__(self, options, PMSroot, path):
        self.options = options
        self.PMSroot = {'main': PMSroot}
        self.path = {'main': path}
    
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
        
        dprint(__name__, 2, "CCmds_getParam: {0}, {1}", param, leftover)
        return [param, leftover]
    
    def getKey(self, src, srcXML, param):
        attrib, leftover = self.getParam(src, param)
        default, leftover = self.getParam(src, leftover)
        
        # get base element
        if attrib.startswith('@'):  # redirect to additional XML
            parts = attrib.split('/',1)
            el = self.PMSroot[parts[0][1:]]
            attrib = parts[1]
        elif attrib.startswith('/'):  # start at root
            el = self.PMSroot['main']
            attrib = attrib[1:]
        else:
            el = src
        
        # walk the path if neccessary
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
        
        dprint(__name__, 2, "CCmds_getKey: {0},{1},{2}", res, leftover,dfltd)
        return [res,leftover,dfltd]
    
    def getElement(self, src, srcXML, param):
        tag, leftover = self.getParam(src, param)
        
        # get base element
        if tag.startswith('@'):  # redirect to additional XML
            parts = tag.split('/',1)
            el = self.PMSroot[parts[0][1:]]
            tag = parts[1]
        elif tag.startswith('/'):  # start at root
            el = self.PMSroot[srcXML]
            tag = tag[1:]
        else:
            el = src
        
        # walk the path if neccessary
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
            parts = conv.split('|')
            for part in parts:
                convstr = part.split('=')
                convlist.append((convstr[0], convstr[1]))
        
        dprint(__name__, 2, "CCmds_getConversion: {0},{1}", convlist, leftover)
        return [convlist, leftover]
    
    def applyConversion(self, val, convlist):
        # apply string conversion            
        if convlist!=[]:
            for part in reversed(sorted(convlist)):
                if val>=part[0]:
                    val = part[1]
                    break
        
        dprint(__name__, 2, "CCmds_applyConversion: {0}", val)
        return val
    
    def applyMath(self, val, math, frmt):
        # apply math function - eval
        try:
            x = eval(val)
            if math!='':
                x = eval(math)
            val = ('{0'+frmt+'}').format(x)
        except:
            dprint(__name__, 0, "CCmds_applyMath: Error in math {0}, frmt {1}", math, frmt)
        # apply format specifier
        
        dprint(__name__, 2, "CCmds_applyMath: {0}", val)
        return val



class CCommandCollection(CCommandHelper):
    # XML TREE modifier commands
    # add new commands to this list!
    def TREE_COPY(self, elem, child, src, srcXML, param):
        tag, param_enbl = self.getParam(src, param)
        
        # get base element
        if tag.startswith('/'):
            src = self.PMSroot[srcXML]
            tag = tag[1:]
        elif tag.startswith('@'):
            parts = tag.split('/',1)
            srcXML = parts[0][1:]
            src = self.PMSroot[srcXML]
            tag = parts[1]
        else:
            pass  # keep src
        
        """
        # walk the src path if neccessary
        while '/' in tag and src!=None:
            parts = tag.split('/',1)
            src = src.find(parts[0])
            tag = parts[1]
            print "---", tag
        """
        
        childToCopy = child
        elem.remove(child)
        
        # duplicate child and add to tree
        for elemSRC in src.findall(tag):
            key = 'COPY'
            if param_enbl!='':
                key, leftover, dfltd = self.getKey(elemSRC, srcXML, param_enbl)
                conv, leftover = self.getConversion(elemSRC, leftover)
                if not dfltd:
                    key = self.applyConversion(key, conv)
            
            if key:
                el = copy.deepcopy(childToCopy)
                XML_ExpandTree(el, elemSRC, srcXML)
                XML_ExpandAllAttrib(el, elemSRC, srcXML)
                elem.append(el)
            
        return True  # tree modified, nodes updated: restart from 1st elem
    
    def TREE_CUT(self, elem, child, src, srcXML, param):
        key, leftover, dfltd = self.getKey(src, srcXML, param)
        conv, leftover = self.getConversion(src, leftover)
        if not dfltd:
            key = self.applyConversion(key, conv)
        if key:
            elem.remove(child)
            return True  # tree modified, node removed: restart from 1st elem
        else:
            return False  # tree unchanged
    
    def TREE_ADDXML(self, elem, child, src, srcXML, param):
        path, leftover = self.getParam(src, param)
        tag, leftover = self.getParam(src, leftover)
        
        PMS = XML_ReadFromURL('address', path)
        self.PMSroot[tag] = PMS.getroot()  # store additional PMS XML
        self.path[tag] = path  # store base path
        
        return False  # tree unchanged (well, source tree yes. but that doesn't count...)
    
    
    
    # XML ATTRIB modifier commands
    # add new commands to this list!
    def ATTRIB_VAL(self, src, srcXML, param):
        key, leftover, dfltd = self.getKey(src, srcXML, param)
        conv, leftover = self.getConversion(src, leftover)
        if not dfltd:
            key = self.applyConversion(key, conv)
        return key
    
    def ATTRIB_EVAL(self, src, srcXML, param):
        key, leftover, dfltd = self.getKey(src, srcXML, param)
        math, leftover = self.getParam(src, leftover)
        frmt, leftover = self.getParam(src, leftover)
        if not dfltd:
            key = self.applyMath(key, math, frmt)
        return key
    
    def ATTRIB_SETTING(self, src, srcXML, param):
        opt, leftover = self.getParam(src, param)
        return g_ATVSettings.getSetting(UDID, opt)
    
    def ATTRIB_ADDPATH(self, src, srcXML, param):
        addpath, leftover, dfltd = self.getKey(src, srcXML, param)
        if addpath.startswith('/'):
            res = addpath
        elif addpath == '':
            res = self.path[srcXML]
        else:
            res = self.path[srcXML]+'/'+addpath
        return res

    def ATTRIB_BIGIMAGEURL(self, src, srcXML, param):
        key, leftover, dfltd = self.getKey(src, srcXML, param)
        return self.imageUrl(self.path[srcXML], key, 512, 512)
    
    def ATTRIB_IMAGEURL(self, src, srcXML, param):
        key, leftover, dfltd = self.getKey(src, srcXML, param)
        return self.imageUrl(self.path[srcXML], key, 384, 384)
            
    def imageUrl(self, path, key, width, height):
        if key.startswith('/'):  # internal full path.
            res = 'http://127.0.0.1:32400' + key
        elif key.startswith('http://'):  # external address
            res = key
        else:
            res = 'http://127.0.0.1:32400' + path + '/' + key
        
        # This is bogus (note the extra path component) but ATV is stupid when it comes to caching images, it doesn't use querystrings.
        # Fortunately PMS is lenient...
        #
        return 'http://' + g_param['Addr_PMS'] + '/photo/:/transcode/%s/?width=%d&height=%d&url=' % (quote_plus(res), width, height) + quote_plus(res)
            
    def ATTRIB_URL(self, src, srcXML, param):
        key, leftover, dfltd = self.getKey(src, srcXML, param)
        if key.startswith('/'):  # internal full path.
            res = 'http://' + g_param['Addr_PMS'] + key
        elif key.startswith('http://'):  # external address
            res = key
        else:  # internal path, add-on
            res = 'http://' + g_param['Addr_PMS'] + self.path[srcXML] + '/' + key
        return res
    
    def ATTRIB_MEDIAURL(self, src, srcXML, param):
        el, leftover = self.getElement(src, srcXML, param)
        
        metadata = el
        if el!=None:  # Video
            el = el.find('Media')
        
        # check "Media" element and get key
        if el!=None:  # Media
            if g_ATVSettings.getSetting(UDID, 'forcedirectplay')=='True' or \
               g_ATVSettings.getSetting(UDID, 'forcetranscode')!='True' and \
               el.get('container','') in ("mov", "mp4", "mpegts") and \
               el.get('videoCodec','') in ("mpeg4", "h264", "drmi") and \
               el.get('audioCodec','') in ("aac", "ac3", "drms"):
                # native aTV media
                res = el.find('Part').get('key','')
            else:
                # request transcoding
                res = metadata.get('key','')
                res = PlexAPI_getTranscodePath(self.options, res)
        else:
            dprint(__name__, 0, "MEDIAPATH - element not found: {0}", params)
            res = 'FILE_NOT_FOUND'  # not found?
        
        if res.startswith('/'):  # internal full path.
            res = 'http://' + g_param['Addr_PMS'] + res
        elif res.startswith('http://'):  # external address
            pass
        else:  # internal path, add-on
            res = 'http://' + g_param['Addr_PMS'] + self.path[srcXML] + res
        return res
    
    def ATTRIB_PLAY_COMMAND(self, src, srcXML, param):
        return "&PlexConnect=Play&PlexUDID=' + atv.device.udid"
    
    def ATTRIB_ADDR_PMS(self, src, srcXML, param):
        return g_param['Addr_PMS']
    
    def ATTRIB_episodestring(self, src, srcXML, param):
        parentIndex, leftover, dfltd = self.getKey(src, srcXML, param)  # getKey "defaults" if nothing found.
        index, leftover, dfltd = self.getKey(src, srcXML, leftover)
        title, leftover, dfltd = self.getKey(src, srcXML, leftover)
        out = "{0:0d}x{1:02d} ".format(int(parentIndex), int(index)) + title
        return out
    
    def ATTRIB_sendToATV(self, src, srcXML, param):
        ratingKey, leftover, dfltd = self.getKey(src, srcXML, param)  # getKey "defaults" if nothing found.
        duration, leftover, dfltd = self.getKey(src, srcXML, leftover)
        out = "atv.sessionStorage['ratingKey']='" + ratingKey + "';atv.sessionStorage['duration']='" + duration + \
              "'" #;atv.sessionStorage['reloadXMLpath']='" + self.path[srcXML] + "'"
        return out 
    
    def ATTRIB_getPath(self, src, srcXML, param):
        return self.path[srcXML] 
    
    def ATTRIB_getDurationString(self, src, srcXML, param):
        duration, leftover, dfltd = self.getKey(src, srcXML, param)
        if len(duration) > 0:
            min = int(duration)/1000/60
            hour = min/60
            min = min%60
            if hour == 0: return "%d Minutes" % (min)
            else: return "%dhr %dmin" % (hour, min)            
            
        return ""
    
    
if __name__=="__main__":
    setParams({'Addr_PMS':'*Addr_PMS*'})

    print "load PMS XML"
    _XML = '<PMS number="1" string="Hello"> \
                <DATA number="42" string="World"></DATA> \
                <DATA string="Sun"></DATA> \
            </PMS>'
    PMSroot = etree.fromstring(_XML)
    PMSTree = etree.ElementTree(PMSroot)
    XML_prettyprint(PMSTree)
    
    print
    print "load aTV XML template"
    _XML = '<aTV> \
                <INFO num="{{VAL(number)}}" str="{{VAL(string)}}">Info</INFO> \
                <FILE str="{{VAL(string)}}" strconv="{{VAL(string::World=big|Moon=small|Sun=huge)}}" num="{{VAL(number:5)}}" numfunc="{{EVAL(number:5:int(x/10):&amp;col;02d)}}"> \
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
    options = {}
    g_CommandCollection = CCommandCollection(options, PMSroot, '/library/sections/')
    XML_ExpandTree(aTVroot, PMSroot, 'main')
    XML_ExpandAllAttrib(aTVroot, PMSroot, 'main')
    del g_CommandCollection
    
    print
    print "resulting aTV XML"
    XML_prettyprint(aTVTree)
    
    print
    #print "store aTV XML"
    #str = XML_prettystring(aTVTree)
    #f=open(sys.path[0]+'/XML/aTV_fromTmpl.xml', 'w')
    #f.write(str)
    #f.close()
