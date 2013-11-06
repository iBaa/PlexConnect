#!/usr/bin/env python

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


import os
import sys
import traceback
import inspect 
import string, cgi, time
import copy  # deepcopy()

try:
    import xml.etree.cElementTree as etree
except ImportError:
    import xml.etree.ElementTree as etree

import time, uuid, hmac, hashlib, base64
from urllib import quote_plus
import urlparse

import Settings, ATVSettings
import PlexAPI
from Debug import *  # dprint(), prettyXML()
import Localize



g_param = {}
def setParams(param):
    global g_param
    g_param = param

g_ATVSettings = None
def setATVSettings(cfg):
    global g_ATVSettings
    g_ATVSettings = cfg



# links to CMD class for module wide usage
g_CommandCollection = None



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



def XML_PlayVideo_ChannelsV1(PMSaddress, path):
    XML = '\
<atv>\n\
  <body>\n\
    <videoPlayer id="com.sample.video-player">\n\
      <httpFileVideoAsset id="' + path + '">\n\
        <mediaURL>http://' + PMSaddress + path + '</mediaURL>\n\
        <title>*title*</title>\n\
        <!--bookmarkTime>{{EVAL(Video/viewOffset:0:int(x/1000))}}</bookmarkTime-->\n\
        <myMetadata>\n\
          <!-- PMS, OSD settings, ... -->\n\
          <addrPMS>http://' + PMSaddress + '</addrPMS>\n\
          <key></key>\n\
          <ratingKey></ratingKey>\n\
          <duration></duration>\n\
          <showClock>False</showClock>\n\
          <timeFormat></timeFormat>\n\
          <clockPosition></clockPosition>\n\
          <overscanAdjust></overscanAdjust>\n\
          <showEndtime>False</showEndtime>\n\
          <accessToken></accessToken>\n\
        </myMetadata>\n\
      </httpFileVideoAsset>\n\
    </videoPlayer>\n\
  </body>\n\
</atv>\n\
';
    dprint(__name__,2 , XML)
    return XML



"""
global list of known aTVs - to look up UDID by IP if needed

parameters:
    udid - from options['PlexConnectUDID']
    ip - from client_address btw options['aTVAddress']
"""
g_ATVList = {}

def declareATV(udid, ip):
    global g_ATVList
    if udid in g_ATVList:
        g_ATVList[udid]['ip'] = ip
    else:
        g_ATVList[udid] = {'ip': ip}

def getATVFromIP(ip):
    # find aTV by IP, return UDID
    for udid in g_ATVList:
        if ip==g_ATVList[udid].get('ip', None):
            return udid
    return None  # IP not found



"""
# XML converter functions
# - translate aTV request and send to PMS
# - receive reply from PMS
# - select XML template
# - translate to aTV XML
"""
def XML_PMS2aTV(PMSaddress, path, options):
    # double check aTV UDID, redo from client IP if needed/possible
    if not 'PlexConnectUDID' in options:
        UDID = getATVFromIP(options['aTVAddress'])
        if UDID:
            options['PlexConnectUDID'] = UDID
    else:
        declareATV(options['PlexConnectUDID'], options['aTVAddress'])  # update with latest info
    
    # double check PMS IP address
    # the hope is: aTV sends either PMS address coded into URL or UDID in options
    if PMSaddress=='':
        if 'PlexConnectUDID' in options:
            UDID = options['PlexConnectUDID']
            PMS_uuid = g_ATVSettings.getSetting(options['PlexConnectUDID'], 'pms_uuid')
            PMSaddress = PlexAPI.getPMSAddress(UDID, PMS_uuid)
            # this doesn't work any more, does it? is it really still used/needed?
    
    # check cmd to work on
    cmd = ''
    if 'PlexConnect' in options:
        cmd = options['PlexConnect']
    dprint(__name__, 1, "PlexConnect Cmd: "+cmd)
    
    # check aTV language setting
    if not 'aTVLanguage' in options:
        dprint(__name__, 1, "no aTVLanguage - pick en")
        options['aTVLanguage'] = 'en'
    
    # XML Template selector
    # - PlexConnect command
    # - path
    # - PMS ViewGroup
    XMLtemplate = ''
    PMS = None
    PMSroot = None
    
    # XML direct request or
    # XMLtemplate defined by solely PlexConnect Cmd
    if path.endswith(".xml"):
        XMLtemplate = path.lstrip('/')
        path = ''  # clear path - we don't need PMS-XML
    
    elif cmd=='Play':
        XMLtemplate = 'PlayVideo.xml'
    
    elif cmd=='PlayVideo_ChannelsV1':
        dprint(__name__, 1, "playing Channels XML Version 1: {0}".format(path))
        UDID = options['PlexConnectUDID']
        PMS_uuid = PlexAPI.getPMSFromAddress(UDID, PMSaddress)
        auth_token = PlexAPI.getPMSProperty(UDID, PMS_uuid, 'accesstoken')
        path = PlexAPI.getDirectVideoPath(path, auth_token)
        return XML_PlayVideo_ChannelsV1(PMSaddress, path)  # direct link, no PMS XML available
    
    elif cmd=='PhotoBrowser':
        XMLtemplate = 'Photo_Browser.xml'
        
    elif cmd=='MoviePreview':
        XMLtemplate = 'MoviePreview.xml'
    
    elif cmd=='MoviePrePlay':
        XMLtemplate = 'MoviePrePlay.xml'
    
    elif cmd=='EpisodePrePlay':
        XMLtemplate = 'EpisodePrePlay.xml'
        
    elif cmd=='ChannelPrePlay':
        XMLtemplate = 'ChannelPrePlay.xml'
    
    elif cmd=='ChannelsVideo':
        XMLtemplate = 'ChannelsVideo.xml'

    elif cmd=='ByFolder':
        XMLtemplate = 'ByFolder.xml'
    
    elif cmd == 'MovieSection':
        XMLtemplate = 'MovieSection.xml'
    
    elif cmd == 'TVSection':
        XMLtemplate = 'TVSection.xml'
    
    elif cmd.find('SectionPreview') != -1:
        XMLtemplate = cmd + '.xml'
    
    elif cmd == 'AllMovies':
        XMLtemplate = 'Movie_'+g_ATVSettings.getSetting(options['PlexConnectUDID'], 'movieview')+'.xml'  
    
    elif cmd == 'MovieSecondary':
        XMLtemplate = 'MovieSecondary.xml'
    
    elif cmd == 'AllShows':
        XMLtemplate = 'Show_'+g_ATVSettings.getSetting(options['PlexConnectUDID'], 'showview')+'.xml'  
          
    elif cmd == 'TVSecondary':
        XMLtemplate = 'TVSecondary.xml'
        
    elif cmd == 'PhotoSecondary':
        XMLtemplate = 'PhotoSecondary.xml'
        
    elif cmd == 'Directory':
        XMLtemplate = 'Directory.xml'
    
    elif cmd == 'DirectoryWithPreview':
        XMLtemplate = 'DirectoryWithPreview.xml'

    elif cmd == 'DirectoryWithPreviewActors':
        XMLtemplate = 'DirectoryWithPreviewActors.xml'
            
    elif cmd=='Settings':
        XMLtemplate = 'Settings.xml'
        path = ''  # clear path - we don't need PMS-XML
    
    elif cmd=='SettingsVideoOSD':
        XMLtemplate = 'Settings_VideoOSD.xml'
        path = ''  # clear path - we don't need PMS-XML
    
    elif cmd=='SettingsMovies':
        XMLtemplate = 'Settings_Movies.xml'
        path = ''  # clear path - we don't need PMS-XML
        
    elif cmd=='SettingsTVShows':
        XMLtemplate = 'Settings_TVShows.xml'
        path = ''  # clear path - we don't need PMS-XML
        
    elif cmd.startswith('SettingsToggle:'):
        opt = cmd[len('SettingsToggle:'):]  # cut command:
        parts = opt.split('+')
        g_ATVSettings.toggleSetting(options['PlexConnectUDID'], parts[0].lower())
        XMLtemplate = parts[1] + ".xml"
        dprint(__name__, 2, "ATVSettings->Toggle: {0} in template: {1}", parts[0], parts[1])
        
        path = ''  # clear path - we don't need PMS-XML
        
    elif cmd==('MyPlexLogin'):
        dprint(__name__, 2, "MyPlex->Logging In...")
        if not 'PlexConnectCredentials' in options:
            return XML_Error('PlexConnect', 'MyPlex Sign In called without Credentials.')
        
        parts = options['PlexConnectCredentials'].split(':',1)        
        (username, auth_token) = PlexAPI.MyPlexSignIn(parts[0], parts[1], options)
        
        UDID = options['PlexConnectUDID']
        g_ATVSettings.setSetting(UDID, 'myplex_user', username)
        g_ATVSettings.setSetting(UDID, 'myplex_auth', auth_token)
        
        XMLtemplate = 'Settings.xml'
        path = ''  # clear path - we don't need PMS-XML
    
    elif cmd=='MyPlexLogout':
        dprint(__name__, 2, "MyPlex->Logging Out...")
        
        UDID = options['PlexConnectUDID']
        auth_token = g_ATVSettings.getSetting(UDID, 'myplex_auth')
        PlexAPI.MyPlexSignOut(auth_token)
        
        g_ATVSettings.setSetting(UDID, 'myplex_user', '')
        g_ATVSettings.setSetting(UDID, 'myplex_auth', '')
        
        XMLtemplate = 'Settings.xml'
        path = ''  # clear path - we don't need PMS-XML
    
    elif cmd.startswith('Discover'):
        UDID = options['PlexConnectUDID']
        auth_token = g_ATVSettings.getSetting(UDID, 'myplex_auth')
        PlexAPI.discoverPMS(UDID, g_param['CSettings'], auth_token)
        
        return XML_Error('PlexConnect', 'Discover!')  # not an error - but aTV won't care anyways.
    
    elif path.startswith('/search?'):
        XMLtemplate = 'Search_Results.xml'
    
    elif path=='/library/sections':
        XMLtemplate = 'Library.xml'
        path = ''
    
    elif path=='/channels/all':
        XMLtemplate = 'Channels.xml'
        path = ''
    
    elif path=='/myplex':
        XMLtemplate = 'MyPlex.xml'
        path = ''
    
    # request PMS XML
    if not path=='':
        if 'PlexConnectUDID' in options:
            UDID = options['PlexConnectUDID']
            PMS_uuid = PlexAPI.getPMSFromAddress(UDID, PMSaddress)
            auth_token = PlexAPI.getPMSProperty(UDID, PMS_uuid, 'accesstoken')
        else:
            auth_token = ''
        
        PMS = PlexAPI.getXMLFromPMS('http://'+PMSaddress, path, options, authtoken=auth_token)
        if PMS==False:
            return XML_Error('PlexConnect', 'No Response from Plex Media Server')
        
        PMSroot = PMS.getroot()
        
        dprint(__name__, 1, "viewGroup: "+PMSroot.get('ViewGroup','None'))
    
    # XMLtemplate defined by PMS XML content
    if path=='':
        pass  # nothing to load
    
    elif not XMLtemplate=='':
        pass  # template already selected
    
    elif PMSroot.get('viewGroup','')=="secondary" and (PMSroot.get('art','').find('movie') != -1 or PMSroot.get('thumb','').find('movie') != -1):
        XMLtemplate = 'MovieSectionTopLevel.xml'
    
    elif PMSroot.get('viewGroup','')=="secondary" and (PMSroot.get('art','').find('show') != -1 or PMSroot.get('thumb','').find('show') != -1):
        XMLtemplate = 'TVSectionTopLevel.xml'
        
    elif PMSroot.get('viewGroup','')=="secondary" and (PMSroot.get('art','').find('photo') != -1 or PMSroot.get('thumb','').find('photo') != -1):
        XMLtemplate = 'PhotoSectionTopLevel.xml'
        
    elif PMSroot.get('viewGroup','')=="secondary":
        XMLtemplate = 'Directory.xml'
    
    elif PMSroot.get('viewGroup','')=='show':
        if PMSroot.get('title2')=='By Folder':
          # By Folder View
          XMLtemplate = 'ByFolder.xml'
        else:
          # TV Show grid view
          XMLtemplate = 'Show_'+g_ATVSettings.getSetting(options['PlexConnectUDID'], 'showview')+'.xml'
        
    elif PMSroot.get('viewGroup','')=='season':
        # TV Season view
        XMLtemplate = 'Season_'+g_ATVSettings.getSetting(options['PlexConnectUDID'], 'seasonview')+'.xml'
        
    elif PMSroot.get('viewGroup','')=='movie':
        if PMSroot.get('title2')=='By Folder':
          # By Folder View
          XMLtemplate = 'ByFolder.xml'
        else:
          # Movie listing
          XMLtemplate = 'Movie_'+g_ATVSettings.getSetting(options['PlexConnectUDID'], 'movieview')+'.xml'
          
    elif PMSroot.get('viewGroup','')=='track':
        XMLtemplate = 'Music_Track.xml'
   
    elif PMSroot.get('viewGroup','')=='episode':
        if PMSroot.get('title2')=='On Deck' or \
           PMSroot.get('title2')=='Recently Viewed Episodes' or \
           PMSroot.get('title2')=='Recently Aired' or \
           PMSroot.get('title2')=='Recently Added':
            # TV On Deck View
            XMLtemplate = 'TV_OnDeck.xml'
        else:
            # TV Episode view
            XMLtemplate = 'Episode.xml'
    
    elif PMSroot.get('viewGroup','')=='photo':
        # Photo listing
        XMLtemplate = 'Photo.xml'
    
    else:
        XMLtemplate = 'Directory.xml'
    
    dprint(__name__, 1, "XMLTemplate: "+XMLtemplate)
    
    # get XMLtemplate
    aTVTree = etree.parse(sys.path[0]+'/assets/templates/'+XMLtemplate)
    aTVroot = aTVTree.getroot()
    
    # convert PMS XML to aTV XML using provided XMLtemplate
    global g_CommandCollection
    g_CommandCollection = CCommandCollection(options, PMSroot, PMSaddress, path)
    XML_ExpandTree(aTVroot, PMSroot, 'main')
    XML_ExpandAllAttrib(aTVroot, PMSroot, 'main')
    del g_CommandCollection
    
    dprint(__name__, 1, "====== generated aTV-XML ======")
    dprint(__name__, 1, prettyXML(aTVTree))
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
            
            # recurse into children
            XML_ExpandTree(child, src, srcXML)
            
            res = XML_ExpandNode(elem, child, src, srcXML, 'TAIL')
            if res==True:  # tree modified: restart from 1st elem
                break  # "for child"
        
        if res==False:  # complete tree parsed with no change, stop recursion
            break  # "while True"



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
                res = getattr(g_CommandCollection, 'TREE_'+cmd)(elem, child, src, srcXML, param)
            except:
                dprint(__name__, 0, "XML_ExpandNode - Error in cmd {0}, line {1}\n{2}", cmd, line, traceback.format_exc())
            
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
                res = getattr(g_CommandCollection, 'ATTRIB_'+cmd)(src, srcXML, param)
                line = line[:cmd_start] + res + line[cmd_end+2:]
                pos = cmd_start+len(res)
            except:
                dprint(__name__, 0, "XML_ExpandLine - Error in {0}\n{1}", line, traceback.format_exc())
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
# Command expander classes
# CCommandHelper():
#     base class to the following, provides basic parsing & evaluation functions
# CCommandCollection():
#     cmds to set up sources (ADDXML, VAR)
#     cmds with effect on the tree structure (COPY, CUT) - must be expanded first
#     cmds dealing with single node keys, text, tail only (VAL, EVAL, ADDR_PMS ,...)
"""
class CCommandHelper():
    def __init__(self, options, PMSroot, PMSaddress, path):
        self.options = options
        self.PMSroot = {'main': PMSroot}
        self.PMSaddress = PMSaddress  # default PMS if nothing else specified
        self.path = {'main': path}
        self.variables = {}
    
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
        
        el, srcXML, attrib = self.getBase(src, srcXML, attrib)         
        
        # walk the path if neccessary
        while '/' in attrib and el!=None:
            parts = attrib.split('/',1)
            if parts[0].startswith('#'):  # internal variable in path
                el = el.find(self.variables[parts[0][1:]])
            elif parts[0].startswith('$'):  # setting
                UDID = self.options['PlexConnectUDID']
                el = el.find(g_ATVSettings.getSetting(UDID, parts[0][1:]))
            elif parts[0].startswith('%'):  # PMS property
                UDID = self.options['PlexConnectUDID']
                PMS_uuid = PlexAPI.getPMSFromAddress(UDID, self.PMSaddress)
                el = el.find(PlexAPI.getPMSProperty(UDID, PMS_uuid, parts[0][1:]))
            else:
                el = el.find(parts[0])
            attrib = parts[1]
        
        # check element and get attribute
        if attrib.startswith('#'):  # internal variable
            res = self.variables[attrib[1:]]
            dfltd = False
        elif attrib.startswith('$'):  # setting
            UDID = self.options['PlexConnectUDID']
            res = g_ATVSettings.getSetting(UDID, attrib[1:])
            dfltd = False
        elif attrib.startswith('%'):  # PMS property
            UDID = self.options['PlexConnectUDID']
            PMS_uuid = PlexAPI.getPMSFromAddress(UDID, self.PMSaddress)
            res = PlexAPI.getPMSProperty(UDID, PMS_uuid, attrib[1:])
            dfltd = False
        elif el!=None and attrib in el.attrib:
            res = el.get(attrib)
            dfltd = False
        
        else:  # path/attribute not found
            res = default
            dfltd = True
        
        dprint(__name__, 2, "CCmds_getKey: {0},{1},{2}", res, leftover,dfltd)
        return [res,leftover,dfltd]
    
    def getElement(self, src, srcXML, param):
        tag, leftover = self.getParam(src, param)
        
        el, srcXML, tag = self.getBase(src, srcXML, tag)
        
        # walk the path if neccessary
        while True:
            parts = tag.split('/',1)
            el = el.find(parts[0])
            if not '/' in tag or el==None:
                break
            tag = parts[1]
        return [el, leftover]
    
    def getBase(self, src, srcXML, param):
        # get base element
        if param.startswith('@'):  # redirect to additional XML
            parts = param.split('/',1)
            srcXML = parts[0][1:]
            src = self.PMSroot[srcXML]
            leftover=''
            if len(parts)>1:
                leftover = parts[1]
        elif param.startswith('/'):  # start at root
            src = self.PMSroot['main']
            leftover = param[1:]
        else:
            leftover = param
        
        return [src, srcXML, leftover]
    
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
            dprint(__name__, 0, "CCmds_applyMath: Error in math {0}, frmt {1}\n{2}", math, frmt, traceback.format_exc())
        # apply format specifier
        
        dprint(__name__, 2, "CCmds_applyMath: {0}", val)
        return val
    
    def _(self, msgid):
        return Localize.getTranslation(self.options['aTVLanguage']).ugettext(msgid)



class CCommandCollection(CCommandHelper):
    # XML TREE modifier commands
    # add new commands to this list!
    def TREE_COPY(self, elem, child, src, srcXML, param):
        tag, param_enbl = self.getParam(src, param)

        src, srcXML, tag = self.getBase(src, srcXML, tag)        
        
        # walk the src path if neccessary
        while '/' in tag and src!=None:
            parts = tag.split('/',1)
            src = src.find(parts[0])
            tag = parts[1]
        
        # find index of child in elem - to keep consistent order
        for ix, el in enumerate(list(elem)):
            if el==child:
                break
        
        # duplicate child and add to tree
        for elemSRC in src.findall(tag):
            key = 'COPY'
            if param_enbl!='':
                key, leftover, dfltd = self.getKey(elemSRC, srcXML, param_enbl)
                conv, leftover = self.getConversion(elemSRC, leftover)
                if not dfltd:
                    key = self.applyConversion(key, conv)
            
            if key:
                el = copy.deepcopy(child)
                XML_ExpandTree(el, elemSRC, srcXML)
                XML_ExpandAllAttrib(el, elemSRC, srcXML)
                
                if el.tag=='__COPY__':
                    for el_child in list(el):
                        elem.insert(ix, el_child)
                        ix += 1
                else:
                    elem.insert(ix, el)
                    ix += 1
        
        # remove template child
        elem.remove(child)
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
        tag, leftover = self.getParam(src, param)
        key, leftover, dfltd = self.getKey(src, srcXML, leftover)
        
        if 'PlexConnectUDID' in self.options:
            UDID = self.options['PlexConnectUDID']
            PMS_uuid = PlexAPI.getPMSFromAddress(UDID, self.PMSaddress)
            auth_token = PlexAPI.getPMSProperty(UDID, PMS_uuid, 'accesstoken')
        else:
            auth_token = ''
        
        if key.startswith('//'):  # local servers signature
            pathstart = key.find('/',3)
            type = key[2:pathstart]
            path = key[pathstart:]
            PMS = PlexAPI.getXMLFromMultiplePMS(UDID, path, type, self.options)
        elif key.startswith('/'):  # internal full path.
            path = key
            PMS = PlexAPI.getXMLFromPMS('http://'+self.PMSaddress, path, self.options, auth_token)
        #elif key.startswith('http://'):  # external address
        #    path = key
        #    hijack = g_param['HostToIntercept']
        #    if hijack in path:
        #        dprint(__name__, 1, "twisting...")
        #        hijack_twisted = hijack[::-1]
        #        path = path.replace(hijack, hijack_twisted)
        #        dprint(__name__, 1, path)
        elif key == '':  # internal path
            path = self.path[srcXML]
            PMS = PlexAPI.getXMLFromPMS('http://'+self.PMSaddress, path, self.options, auth_token)
        else:  # internal path, add-on
            path = self.path[srcXML] + '/' + key
            PMS = PlexAPI.getXMLFromPMS('http://'+self.PMSaddress, path, self.options, auth_token)
        
        self.PMSroot[tag] = PMS.getroot()  # store additional PMS XML
        self.path[tag] = path  # store base path
        
        return False  # tree unchanged (well, source tree yes. but that doesn't count...)
    
    def TREE_VAR(self, elem, child, src, srcXML, param):
        var, leftover = self.getParam(src, param)
        key, leftover, dfltd = self.getKey(src, srcXML, leftover)
        conv, leftover = self.getConversion(src, leftover)
        if not dfltd:
            key = self.applyConversion(key, conv)
        
        self.variables[var] = key
        return False  # tree unchanged
    
    
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

    def ATTRIB_SVAL(self, src, srcXML, param):
        key, leftover, dfltd = self.getKey(src, srcXML, param)
        conv, leftover = self.getConversion(src, leftover)
        if not dfltd:
            key = self.applyConversion(key, conv)
        return quote_plus(key)

    def ATTRIB_SETTING(self, src, srcXML, param):
        opt, leftover = self.getParam(src, param)
        UDID = self.options['PlexConnectUDID']
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
    
    def ATTRIB_IMAGEURL(self, src, srcXML, param):
        key, leftover, dfltd = self.getKey(src, srcXML, param)
        width, leftover = self.getParam(src, leftover)
        height, leftover = self.getParam(src, leftover)
        if height=='':
            height = width
        
        PMSaddress = self.PMSaddress
        cmd_start = key.find('PMS(')
        cmd_end = key.find(')', cmd_start)
        if cmd_start>-1 and cmd_end>-1 and cmd_end>cmd_start:
            PMSaddress = key[cmd_start+4:cmd_end]
            key = key[cmd_end+1:]
        
        UDID = self.options['PlexConnectUDID']
        PMS_uuid = PlexAPI.getPMSFromAddress(UDID, PMSaddress)
        AuthToken = PlexAPI.getPMSProperty(UDID, PMS_uuid, 'accesstoken')
        
        if width=='':
            # direct play
            res = PlexAPI.getDirectImagePath(key, AuthToken)
        else:
            # request transcoding
            res = PlexAPI.getTranscodeImagePath(key, AuthToken, self.path[srcXML], width, height)
        
        if res.startswith('/'):  # internal full path.
            res = 'http://' + PMSaddress + res
        elif res.startswith('http://'):  # external address
            pass
        else:  # internal path, add-on
            res = 'http://' + PMSaddress + self.path[srcXML] + '/' + res
        
        dprint(__name__, 1, 'ImageURL: {0}', res)
        return res
    
    def ATTRIB_MUSICURL(self, src, srcXML, param):
        key, leftover, dfltd = self.getKey(src, srcXML, param)
        
        UDID = self.options['PlexConnectUDID']
        PMS_uuid = PlexAPI.getPMSFromAddress(UDID, self.PMSaddress)
        AuthToken = PlexAPI.getPMSProperty(UDID, PMS_uuid, 'accesstoken')
        
        # direct play
        res = PlexAPI.getDirectAudioPath(key, AuthToken)
        
        if res.startswith('/'):  # internal full path.
            res = 'http://' + self.PMSaddress + res
        elif res.startswith('http://'):  # external address
            hijack = g_param['HostToIntercept']
            if hijack in res:
                dprint(__name__, 1, "twisting...")
                hijack_twisted = hijack[::-1]
                res = res.replace(hijack, hijack_twisted)
                dprint(__name__, 1, res)
        else:  # internal path, add-on
            res = 'http://' + self.PMSaddress + self.path[srcXML] + '/' + res
        
        dprint(__name__, 1, 'MusicURL: {0}', res)
        return res
    
    def ATTRIB_URL(self, src, srcXML, param):
        key, leftover, dfltd = self.getKey(src, srcXML, param)
        
        PMSaddress = self.PMSaddress
        cmd_start = key.find('PMS(')
        cmd_end = key.find(')', cmd_start)
        if cmd_start>-1 and cmd_end>-1 and cmd_end>cmd_start:
            PMSaddress = key[cmd_start+4:cmd_end]
            key = key[cmd_end+1:]
        
        if not PMSaddress=='':
            PMSaddress = '/PMS(' + quote_plus(PMSaddress) + ')'
        
        res = 'http://' + g_param['HostOfPlexConnect']  # base address to PlexConnect
        
        if key.endswith('.js'):  # link to PlexConnect owned .js stuff
            res = res + key
        elif key.startswith('http://'):  # external server
            res = key
            """
            parts = urlparse.urlsplit(key)  # (scheme, networklocation, path, ...)
            key = urlparse.urlunsplit(('', '', parts[2], parts[3], parts[4]))  # keep path only
            PMS_uuid = PlexAPI.getPMSFromIP(g_param['PMS_list'], parts.hostname)
            PMSaddress = PlexAPI.getAddress(g_param['PMS_list'], PMS_uuid)  # get PMS address (might be local as well!?!)
            res = res + '/PMS(' + quote_plus(PMSaddress) + ')' + key
            """
        elif key.startswith('/'):  # internal full path.
            res = res + PMSaddress + key
        elif key == '':  # internal path
            res = res + PMSaddress + self.path[srcXML]
        else:  # internal path, add-on
            res = res + PMSaddress + self.path[srcXML] + '/' + key
        
        return res
    
    def ATTRIB_MEDIAURL(self, src, srcXML, param):
        Video, leftover = self.getElement(src, srcXML, param)
        
        UDID = self.options['PlexConnectUDID']
        PMS_uuid = PlexAPI.getPMSFromAddress(UDID, self.PMSaddress)
        AuthToken = PlexAPI.getPMSProperty(UDID, PMS_uuid, 'accesstoken')
        
        if not Video:
            # not a complete video structure - take key directly and build direct-play path
            key, leftover, dfltd = self.getKey(src, srcXML, param)
            res = PlexAPI.getDirectVideoPath(key, AuthToken)
            res = PlexAPI.getURL('http://'+self.PMSaddress, self.path[srcXML], res)
            return res
        
        # complete video structure - request transcoding if needed
        Media = Video.find('Media')
        
        # check "Media" element and get key
        if Media!=None:
            # transcoder action
            transcoderAction = g_ATVSettings.getSetting(UDID, 'transcoderaction')
            
            # quality limits: quality=(resolution, quality, bitrate)
            qLookup = { '480p 2.0Mbps' :('720x480', '60', '2000'), \
                        '720p 3.0Mbps' :('1280x720', '75', '3000'), \
                        '720p 4.0Mbps' :('1280x720', '100', '4000'), \
                        '1080p 8.0Mbps' :('1920x1080', '60', '8000'), \
                        '1080p 10.0Mbps' :('1920x1080', '75', '10000'), \
                        '1080p 12.0Mbps' :('1920x1080', '90', '12000'), \
                        '1080p 20.0Mbps' :('1920x1080', '100', '20000'), \
                        '1080p 40.0Mbps' :('1920x1080', '100', '40000') }
            if PlexAPI.getPMSProperty(UDID, PMS_uuid, 'type')=='local':
                qLimits = qLookup[g_ATVSettings.getSetting(UDID, 'transcodequality')]
            else:
                qLimits = qLookup[g_ATVSettings.getSetting(UDID, 'remotebitrate')]
            
            if transcoderAction=='DirectPlay' \
               or \
               transcoderAction=='Auto' and \
               Media.get('protocol','-') in ("hls") and \
               int(Media.get('bitrate','0')) < int(qLimits[2]) \
               or \
               transcoderAction=='Auto' and \
               Media.get('container','-') in ("mov", "mp4") and \
               Media.get('videoCodec','-') in ("mpeg4", "h264", "drmi") and \
               Media.get('audioCodec','-') in ("aac", "ac3", "drms") and \
               int(Media.get('bitrate','0')) < int(qLimits[2]):
                # direct play for...
                #    force direct play
                # or HTTP live stream (limited by quality setting)
                # or native aTV media (limited by quality setting)
                res, leftover, dfltd = self.getKey(Media, srcXML, 'Part/key')
                
                if Media.get('indirect', False):  # indirect... todo: select suitable resolution, today we just take first Media
                    PMS = PlexAPI.getXMLFromPMS('http://'+self.PMSaddress, res, self.options, AuthToken)  # todo... check key for trailing '/' or even 'http'
                    res, leftover, dfltd = self.getKey(PMS.getroot(), srcXML, 'Video/Media/Part/key')
                
                res = PlexAPI.getDirectVideoPath(res, AuthToken)
                print "directplay"
            else:
                # request transcoding
                res = Video.get('key','')
                
                # misc settings: subtitlesize, audioboost
                settings = ( g_ATVSettings.getSetting(UDID, 'subtitlesize'), \
                             g_ATVSettings.getSetting(UDID, 'audioboost') )
                print "transcode"
                res = PlexAPI.getTranscodeVideoPath(res, AuthToken, self.options, transcoderAction, qLimits, settings)
        
        else:
            dprint(__name__, 0, "MEDIAPATH - element not found: {0}", param)
            res = 'FILE_NOT_FOUND'  # not found?
        
        if res.startswith('/'):  # internal full path.
            res = 'http://' + self.PMSaddress + res
        elif res.startswith('http://'):  # external address
            hijack = g_param['HostToIntercept']
            if hijack in res:
                dprint(__name__, 1, "twisting...")
                hijack_twisted = hijack[::-1]
                res = res.replace(hijack, hijack_twisted)
                dprint(__name__, 1, res)
        else:  # internal path, add-on
            res = 'http://' + self.PMSaddress + self.path[srcXML] + res
        
        dprint(__name__, 1, 'MediaURL: {0}', res)
        return res
            
    def ATTRIB_ADDR_PMS(self, src, srcXML, param):
        if param == 'URL':
            UDID = self.options['PlexConnectUDID']
            uuid = PlexAPI.getPMSFromAddress(UDID, self.PMSaddress)
            if not PlexAPI.isPMSOwned(UDID, uuid):
                local = PlexAPI.getLocalPMSAddress(UDID)
                if local != '':
                    return local
        return self.PMSaddress
    
    def ATTRIB_episodestring(self, src, srcXML, param):
        parentIndex, leftover, dfltd = self.getKey(src, srcXML, param)  # getKey "defaults" if nothing found.
        index, leftover, dfltd = self.getKey(src, srcXML, leftover)
        title, leftover, dfltd = self.getKey(src, srcXML, leftover)
        out = self._("{0:0d}x{1:02d} {2}").format(int(parentIndex), int(index), title)
        return out
    
    def ATTRIB_getDurationString(self, src, srcXML, param):
        duration, leftover, dfltd = self.getKey(src, srcXML, param)
        min = int(duration)/1000/60
        UDID = self.options['PlexConnectUDID']
        if g_ATVSettings.getSetting(UDID, 'durationformat') == 'Minutes':
            return self._("{0:d} Minutes").format(min)
        else:
            if len(duration) > 0:
                hour = min/60
                min = min%60
                if hour == 0: return self._("{0:d} Minutes").format(min)
                else: return self._("{0:d}hr {1:d}min").format(hour, min)
        return ""
    
    def ATTRIB_contentRating(self, src, srcXML, param):
        rating, leftover, dfltd = self.getKey(src, srcXML, param)
        if rating.find('/') != -1:
            parts = rating.split('/')
            return parts[1]
        else:
            return rating
        
    def ATTRIB_unwatchedCountGrid(self, src, srcXML, param):
        total, leftover, dfltd = self.getKey(src, srcXML, param)
        viewed, leftover, dfltd = self.getKey(src, srcXML, leftover)
        unwatched = int(total) - int(viewed)
        return str(unwatched)
    
    def ATTRIB_unwatchedCountList(self, src, srcXML, param):
        total, leftover, dfltd = self.getKey(src, srcXML, param)
        viewed, leftover, dfltd = self.getKey(src, srcXML, leftover)
        unwatched = int(total) - int(viewed)
        if unwatched > 0: return self._("{0} unwatched").format(unwatched)
        else: return ""
    
    def ATTRIB_TEXT(self, src, srcXML, param):
        return self._(param)
    
    def ATTRIB_PMSCOUNT(self, src, srcXML, param):
        UDID = self.options['PlexConnectUDID']
        return str(PlexAPI.getPMSCount(UDID))
    
    def ATTRIB_PMSNAME(self, src, srcXML, param):
        UDID = self.options['PlexConnectUDID']
        PMS_uuid = PlexAPI.getPMSFromAddress(UDID, self.PMSaddress)
        PMS_name = PlexAPI.getPMSProperty(UDID, PMS_uuid, 'name')
        if PMS_name=='':
            return "No Server in Proximity"
        else:
            return PMS_name



if __name__=="__main__":
    cfg = Settings.CSettings()
    param = {}
    param['CSettings'] = cfg
    
    param['Addr_PMS'] = '*Addr_PMS*'
    param['HostToIntercept'] = 'trailers.apple.com'
    setParams(param)
    
    cfg = ATVSettings.CATVSettings()
    setATVSettings(cfg)
    
    print "load PMS XML"
    _XML = '<PMS number="1" string="Hello"> \
                <DATA number="42" string="World"></DATA> \
                <DATA string="Sun"></DATA> \
            </PMS>'
    PMSroot = etree.fromstring(_XML)
    PMSTree = etree.ElementTree(PMSroot)
    print prettyXML(PMSTree)
    
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
    print prettyXML(aTVTree)
    
    print
    print "unpack PlexConnect COPY/CUT commands"
    options = {}
    options['PlexConnectUDID'] = '007'
    g_CommandCollection = CCommandCollection(options, PMSroot, '/library/sections/')
    XML_ExpandTree(aTVroot, PMSroot, 'main')
    XML_ExpandAllAttrib(aTVroot, PMSroot, 'main')
    del g_CommandCollection
    
    print
    print "resulting aTV XML"
    print prettyXML(aTVTree)
    
    print
    #print "store aTV XML"
    #str = prettyXML(aTVTree)
    #f=open(sys.path[0]+'/XML/aTV_fromTmpl.xml', 'w')
    #f.write(str)
    #f.close()
    
    del cfg
