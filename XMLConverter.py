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
import string, random
import copy  # deepcopy()

import json
import datetime

try:
    import xml.etree.cElementTree as etree
except ImportError:
    import xml.etree.ElementTree as etree

import time, uuid, hmac, hashlib, base64
from urllib import quote_plus, unquote_plus, urlencode
import urllib2
import urlparse

from Version import __VERSION__  # for {{EVAL()}}, display in settings page
import Settings, ATVSettings
import PlexAPI
from Debug import *  # dprint(), prettyXML()
import Localize

import PILBackgrounds
from PILBackgrounds import isPILinstalled

g_param = {}
def setParams(param):
    global g_param
    g_param = param

g_ATVSettings = None
def setATVSettings(cfg):
    global g_ATVSettings
    g_ATVSettings = cfg



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



def XML_PlayVideo_ChannelsV1(baseURL, path):
    XML = '\
<atv>\n\
  <body>\n\
    <videoPlayer id="com.sample.video-player">\n\
      <httpFileVideoAsset id="' + path + '">\n\
        <mediaURL>' + baseURL + path + '</mediaURL>\n\
        <title>*title*</title>\n\
        <!--bookmarkTime>{{EVAL(int({{VAL(Video/viewOffset:0)}}/1000))}}</bookmarkTime-->\n\
        <videoPlayerSettings>\n\
          <!-- PMS, OSD settings, ... -->\n\
          <baseURL>' + baseURL + '</baseURL>\n\
          <accessToken></accessToken>\n\
          <showClock>False</showClock>\n\
          <timeFormat></timeFormat>\n\
          <clockPosition></clockPosition>\n\
          <overscanAdjust></overscanAdjust>\n\
          <showEndtime>False</showEndtime>\n\
          <subtitleSize></subtitleSize>\n\
        </videoPlayerSettings>\n\
        <myMetadata>\n\
          <key></key>\n\
          <ratingKey></ratingKey>\n\
          <duration></duration>\n\
          <subtitleURL></subtitleURL>\n\
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
def XML_PMS2aTV(PMS_address, path, options):
    # double check aTV UDID, redo from client IP if needed/possible
    if not 'PlexConnectUDID' in options:
        UDID = getATVFromIP(options['aTVAddress'])
        if UDID:
            options['PlexConnectUDID'] = UDID
        else:
            # aTV unidentified, UDID not known    
            return XML_Error('PlexConnect','Unexpected error - unidentified ATV')
    else:
        declareATV(options['PlexConnectUDID'], options['aTVAddress'])  # update with latest info
    
    UDID = options['PlexConnectUDID']
    
    # determine PMS_uuid, PMSBaseURL from IP (PMS_mark)
    PMS_uuid = PlexAPI.getPMSFromAddress(UDID, PMS_address)
    PMS_baseURL = PlexAPI.getPMSProperty(UDID, PMS_uuid, 'baseURL')
    
    # check cmd to work on
    cmd = ''
    dir = ''
    channelsearchURL = ''
    
    if 'PlexConnect' in options:
        cmd = options['PlexConnect']
    
    dprint(__name__, 1, "---------------------------------------------")
    dprint(__name__, 1, "PMS, path: {0} {1} ", PMS_address, path)
    dprint(__name__, 1, "Initial Command: {0}", cmd)
    
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

    # Deal with any special commands
    if cmd.startswith('SettingsToggle:'):
        opt = cmd[len('SettingsToggle:'):]  # cut command:
        parts = opt.split('+')
        g_ATVSettings.toggleSetting(options['PlexConnectUDID'], parts[0].lower())
        parts1 = parts[1].split('_', 1)
        dir = parts1[0]
        cmd = parts1[1]
        XMLtemplate = dir + '/' + cmd + '.xml'
        dprint(__name__, 2, "ATVSettings->Toggle: {0} in template: {1}", parts[0], parts[1])
        path = ''  # clear path - we don't need PMS-XML  
    
    elif cmd=='SaveSettings':
        g_ATVSettings.saveSettings();
        return XML_Error('PlexConnect', 'SaveSettings!')  # not an error - but aTV won't care anyways.
        
    elif cmd=='PlayVideo_ChannelsV1':
        dprint(__name__, 1, "playing Channels XML Version 1: {0}".format(path))
        auth_token = PlexAPI.getPMSProperty(UDID, PMS_uuid, 'accesstoken')
        path = PlexAPI.getDirectVideoPath(path, auth_token)
        return XML_PlayVideo_ChannelsV1(PMS_baseURL, path)  # direct link, no PMS XML available
    
    elif cmd=='PlayTrailer':
        trailerID = options['PlexConnectTrailerID']
        info = urllib2.urlopen("https://youtube.com/get_video_info?html5=1&video_id=" + trailerID).read()
        parsed = urlparse.parse_qs(info)
        
        key = 'player_response'
        if not key in parsed:
            return XML_Error('PlexConnect', 'Youtube: No Trailer Info available')
        streams_dict = json.loads(parsed[key][0])
	streams = streams_dict['streamingData']['formats']
        
        url = ''
        for i in range(len(streams)):
            stream = streams[i]
	    # 18: "medium", 22: hd720
            if stream['itag'] == 18:
                url = stream['url']
	    # if there is also a "22" (720p) stream, let's upgrade to that one
            if stream['itag'] == 22:
                url = stream['url']
        if url == '':
            return XML_Error('PlexConnect','Youtube: ATV compatible Trailer not available')
        
        return XML_PlayVideo_ChannelsV1('', url.replace('&','&amp;'))
        
    elif cmd=='MyPlexLogin':
        dprint(__name__, 2, "MyPlex->Logging In...")
        if not 'PlexConnectCredentials' in options:
            return XML_Error('PlexConnect', 'MyPlex Sign In called without Credentials.')
        
        parts = options['PlexConnectCredentials'].split(':',1)        
        (username, auth_token) = PlexAPI.MyPlexSignIn(parts[0], parts[1], options)
        PlexAPI.discoverPMS(UDID, g_param['CSettings'], g_param['IP_self'], {'MyPlex': auth_token})
        
        g_ATVSettings.setSetting(UDID, 'myplex_user', username)
        g_ATVSettings.setSetting(UDID, 'myplex_auth', auth_token)
        g_ATVSettings.setSetting(UDID, 'plexhome_enable', 'False')
        g_ATVSettings.setSetting(UDID, 'plexhome_user', '')
        g_ATVSettings.setSetting(UDID, 'plexhome_auth', '')
        
        XMLtemplate = 'Settings/Main.xml'
        path = ''  # clear path - we don't need PMS-XML
    
    elif cmd=='MyPlexLogout':
        dprint(__name__, 2, "MyPlex->Logging Out...")
        
        auth_token = g_ATVSettings.getSetting(UDID, 'myplex_auth')
        PlexAPI.MyPlexSignOut(auth_token)
        PlexAPI.discoverPMS(UDID, g_param['CSettings'], g_param['IP_self'], {'MyPlex': ''})
        
        g_ATVSettings.setSetting(UDID, 'myplex_user', '')
        g_ATVSettings.setSetting(UDID, 'myplex_auth', '')
        g_ATVSettings.setSetting(UDID, 'plexhome_enable', 'False')
        g_ATVSettings.setSetting(UDID, 'plexhome_user', '')
        g_ATVSettings.setSetting(UDID, 'plexhome_auth', '')
        
        XMLtemplate = 'Settings/Main.xml'
        path = ''  # clear path - we don't need PMS-XML
    
    elif cmd=='MyPlexSwitchHomeUser':
        dprint(__name__, 2, "MyPlex->switch HomeUser...")
        if not 'PlexConnectCredentials' in options:
            return XML_Error('PlexConnect', 'MyPlex HomeUser called without Credentials.')
        
        parts = options['PlexConnectCredentials'].split(':',1)
        if len(parts)!=2:
            return XML_Error('PlexConnect', 'MyPlex HomeUser called with bad Credentials.')
        
        auth_token = g_ATVSettings.getSetting(UDID, 'myplex_auth')
        (plexHome_user, plexHome_auth) = PlexAPI.MyPlexSwitchHomeUser(parts[0], parts[1], options, auth_token)
        PlexAPI.discoverPMS(UDID, g_param['CSettings'], g_param['IP_self'], {'MyPlex': auth_token, 'PlexHome': plexHome_auth})
        
        g_ATVSettings.setSetting(UDID, 'plexhome_enable', 'True')
        g_ATVSettings.setSetting(UDID, 'plexhome_user', plexHome_user)
        g_ATVSettings.setSetting(UDID, 'plexhome_auth', plexHome_auth)
        
        XMLtemplate = 'Settings/PlexHome.xml'
    
    elif cmd=='MyPlexLogoutHomeUser':
        dprint(__name__, 2, "MyPlex->Logging Out HomeUser...")
        
        auth_token = g_ATVSettings.getSetting(UDID, 'myplex_auth')
        PlexAPI.discoverPMS(UDID, g_param['CSettings'], g_param['IP_self'], {'MyPlex': auth_token, 'PlexHome': ''})
        
        g_ATVSettings.setSetting(UDID, 'plexhome_enable', 'True')  # stays at PlexHome mode
        g_ATVSettings.setSetting(UDID, 'plexhome_user', '')
        g_ATVSettings.setSetting(UDID, 'plexhome_auth', '')
        
        XMLtemplate = 'Settings/PlexHome.xml'
    
    elif cmd=='MyPlexLeaveHome':
        dprint(__name__, 2, "MyPlex->Leave Home...")
        
        auth_token = g_ATVSettings.getSetting(UDID, 'myplex_auth')
        PlexAPI.discoverPMS(UDID, g_param['CSettings'], g_param['IP_self'], {'MyPlex': auth_token})
        
        g_ATVSettings.setSetting(UDID, 'plexhome_enable', 'False')  # exit PlexHome mode completely
        g_ATVSettings.setSetting(UDID, 'plexhome_user', '')
        g_ATVSettings.setSetting(UDID, 'plexhome_auth', '')
        
        XMLtemplate = 'Settings/PlexHome.xml'
    
    elif cmd.startswith('Discover'):
        tokenDict = {}
        tokenDict['MyPlex'] = g_ATVSettings.getSetting(UDID, 'myplex_auth')
        if g_ATVSettings.getSetting(UDID, 'plexhome_enable') == 'True':
            tokenDict['PlexHome'] = g_ATVSettings.getSetting(UDID, 'plexhome_auth')
        PlexAPI.discoverPMS(UDID, g_param['CSettings'], g_param['IP_self'], tokenDict)
        
        # sanitize aTV settings from not-working combinations
        # fanart only with PIL/pillow installed, only with iOS>=6.0  # watch out: this check will make trouble with iOS10
        if not PILBackgrounds.isPILinstalled() or \
           not options['aTVFirmwareVersion'] >= '6.0':
            dprint(__name__, 2, "disable fanart (PIL not installed or aTVFirmwareVersion<6.0)")
            g_ATVSettings.setSetting(UDID, 'fanart', 'Hide')
        
        return XML_Error('PlexConnect', 'Discover!')  # not an error - but aTV won't care anyways.
    
    elif path.find('serviceSearch') != -1 or (path.find('video') != -1 and path.lower().find('search') != -1):
        XMLtemplate = 'Channels/VideoSearchResults.xml'
    
    elif path.find('SearchResults') != -1:
        XMLtemplate = 'Channels/VideoSearchResults.xml'

    # Special case scanners
    if cmd=='S_-_BABS' or cmd=='BABS':
        dprint(__name__, 1, "Found S - BABS / BABS")
        dir = 'TVShow'
        cmd = 'NavigationBar'
    elif cmd=='Plex_Music':
        dprint(__name__, 1, "Found Plex_Music")
        dir = 'Music'
        cmd = 'NavigationBar'
    elif cmd=='Plex_Movie':
        dprint(__name__, 1, "Found Plex_Movie")
        dir = 'Movie'
        cmd = 'NavigationBar'
    elif cmd=='Plex_TV_Series':
        dprint(__name__, 1, "Found Plex_TV_Series")
        dir = 'TVShow'
        cmd = 'NavigationBar'
    elif cmd.find('Scanner') != -1:
        dprint(__name__, 1, "Found Scanner.")
        if cmd.find('Series') != -1: dir = 'TVShow'
        elif cmd.find('Movie') != -1: dir = 'Movie'
        elif cmd.find('Video') != -1 or cmd.find('Personal_Media') != -1:
            # Plex Video Files Scanner
            # Extended Personal Media Scanner
            dir = 'HomeVideo'
        elif cmd.find('Photo') != -1: dir = 'Photo'
        elif cmd.find('Premium_Music') != -1: dir = 'Music'
        elif cmd.find('Music') != -1 or cmd.find('iTunes') != -1: dir ='Music'
        elif cmd.find('LiveTV') != -1: dir = 'LiveTV'
        else:
            return XML_Error('PlexConnect', 'Unknown scanner: '+cmd)
        
        cmd = 'NavigationBar'
    # Not a special command so split it 
    elif cmd.find('_') != -1:
        parts = cmd.split('_', 1)
        dir = parts[0]
        cmd = parts[1]

    # Commands that contain a directory
    if dir != '':
        XMLtemplate = dir + '/' + cmd + '.xml'
        if path == '/': path = ''
    
    dprint(__name__, 1, "Split Directory: {0} Command: {1}", dir, cmd)
    dprint(__name__, 1, "XMLTemplate: {0}", XMLtemplate)
    dprint(__name__, 1, "---------------------------------------------")
    
    PMSroot = None
    while True:
        # request PMS-XML
        if not path=='' and not PMSroot and PMS_address:
            if PMS_address in ['all', 'owned', 'shared', 'local', 'remote']:
                # owned, shared PMSs
                type = PMS_address
                PMS = PlexAPI.getXMLFromMultiplePMS(UDID, path, type, options)
            else:
                # IP:port or plex.tv
                # PMS_uuid derived earlier from PMSaddress
                auth_token = PlexAPI.getPMSProperty(UDID, PMS_uuid, 'accesstoken')
                enableGzip = PlexAPI.getPMSProperty(UDID, PMS_uuid, 'enableGzip')
                PMS = PlexAPI.getXMLFromPMS(PMS_baseURL, path, options, auth_token, enableGzip)
            
            if PMS==False:
                return XML_Error('PlexConnect', 'No Response from Plex Media Server')
            
            PMSroot = PMS.getroot()
        
        # get XMLtemplate
        aTVTree = etree.parse(sys.path[0]+'/assets/templates/'+XMLtemplate)
        aTVroot = aTVTree.getroot()
        
        # convert PMS XML to aTV XML using provided XMLtemplate
        CommandCollection = CCommandCollection(options, PMSroot, PMS_address, path)
        XML_ExpandTree(CommandCollection, aTVroot, PMSroot, 'main')
        XML_ExpandAllAttrib(CommandCollection, aTVroot, PMSroot, 'main')
        del CommandCollection
        
        # no redirect? exit loop!
        redirect = aTVroot.find('redirect')
        if redirect==None:
            break;
            
        # redirect to new PMS-XML - if necessary
        path_rdrct = redirect.get('newPath')
        if path_rdrct:
            path = path_rdrct
            PMSroot = None  # force PMS-XML reload
            dprint(__name__, 1, "PMS-XML redirect: {0}", path)
        
        # redirect to new XMLtemplate - if necessary
        XMLtemplate_rdrct = redirect.get('template')
        if XMLtemplate_rdrct:
            XMLtemplate = XMLtemplate_rdrct.replace(" ", "")
            dprint(__name__, 1, "XMLTemplate redirect: {0}", XMLtemplate)
    
        dprint(__name__, 1, "====== generated aTV-XML ======")
        dprint(__name__, 1, aTVroot)
        dprint(__name__, 1, "====== aTV-XML finished ======")
    dprint(__name__, 1, "====== generated aTV-XML ======")
    dprint(__name__, 1, aTVroot)
    dprint(__name__, 1, "====== aTV-XML finished ======")
    
    return etree.tostring(aTVroot)



def XML_ExpandTree(CommandCollection, elem, src, srcXML):
    # unpack template 'COPY'/'CUT' command in children
    res = False
    while True:
        if list(elem)==[]:  # no sub-elements, stop recursion
            break
        
        for child in elem:
            res = XML_ExpandNode(CommandCollection, elem, child, src, srcXML, 'TEXT')
            if res==True:  # tree modified: restart from 1st elem
                break  # "for child"
            
            # recurse into children
            XML_ExpandTree(CommandCollection, child, src, srcXML)
            
            res = XML_ExpandNode(CommandCollection, elem, child, src, srcXML, 'TAIL')
            if res==True:  # tree modified: restart from 1st elem
                break  # "for child"
        
        if res==False:  # complete tree parsed with no change, stop recursion
            break  # "while True"



def XML_ExpandNode(CommandCollection, elem, child, src, srcXML, text_tail):
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
        next_start = line.find('{{',cmd_start+2)
        while next_start!=-1 and next_start<cmd_end:
            cmd_end = line.find('}}',cmd_end+2)
            next_start = line.find('{{',next_start+2)
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
                param = XML_ExpandLine(CommandCollection, src, srcXML, param)  # expand any attributes in the parameter
                res = getattr(CommandCollection, 'TREE_'+cmd)(elem, child, src, srcXML, param)
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



def XML_ExpandAllAttrib(CommandCollection, elem, src, srcXML):
    # unpack template commands in elem.text
    line = elem.text
    if line!=None:
        elem.text = XML_ExpandLine(CommandCollection, src, srcXML, line.strip())
    
    # unpack template commands in elem.tail
    line = elem.tail
    if line!=None:
        elem.tail = XML_ExpandLine(CommandCollection, src, srcXML, line.strip())
    
    # unpack template commands in elem.attrib.value
    for attrib in elem.attrib:
        line = elem.get(attrib)
        elem.set(attrib, XML_ExpandLine(CommandCollection, src, srcXML, line.strip()))
    
    # recurse into children
    for el in elem:
        XML_ExpandAllAttrib(CommandCollection, el, src, srcXML)



def XML_ExpandLine(CommandCollection, src, srcXML, line):
    pos = 0
    while True:
        cmd_start = line.find('{{',pos)
        cmd_end   = line.find('}}',pos)
        next_start = line.find('{{',cmd_start+2)
        while next_start!=-1 and next_start<cmd_end:
            cmd_end = line.find('}}',cmd_end+2)
            next_start = line.find('{{',next_start+2)

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
                param = XML_ExpandLine(CommandCollection, src, srcXML, param)  # expand any attributes in the parameter
                res = getattr(CommandCollection, 'ATTRIB_'+cmd)(src, srcXML, param)
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
    def __init__(self, options, PMSroot, PMS_address, path):
        self.options = options
        self.PMSroot = {'main': PMSroot}
        self.PMS_address = PMS_address  # default PMS if nothing else specified
        self.path = {'main': path}
        
        self.ATV_udid = options['PlexConnectUDID']
        self.PMS_uuid = PlexAPI.getPMSFromAddress(self.ATV_udid, PMS_address)
        self.PMS_baseURL = PlexAPI.getPMSProperty(self.ATV_udid, self.PMS_uuid, 'baseURL')
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

        sevenDate = datetime.datetime.now().replace(hour=19)
        elevenDate = datetime.datetime.now().replace(hour=23)

        param = param.replace("7pmtimestamp", str(int(time.mktime(sevenDate.timetuple()))))
        param = param.replace("11pmtimestamp", str(int(time.mktime(elevenDate.timetuple()))))
        
        dprint(__name__, 2, "CCmds_getParam: {0}, {1}", param, leftover)
        return [param, leftover]
    
    def getKey(self, src, srcXML, param):
        attrib, leftover = self.getParam(src, param)
        default, leftover = self.getParam(src, leftover)
        
        el, srcXML, attrib = self.getBase(src, srcXML, attrib)         
        
        # walk the path if neccessary
        while '/' in attrib and el!=None:
            parts = attrib.split('/',1)
            if parts[0].startswith('#') and attrib[1:] in self.variables:  # internal variable in path
                el = el.find(self.variables[parts[0][1:]])
            elif parts[0].startswith('$'):  # setting
                el = el.find(g_ATVSettings.getSetting(self.ATV_udid, parts[0][1:]))
            elif parts[0].startswith('%'):  # PMS property
                el = el.find(PlexAPI.getPMSProperty(self.ATV_udid, self.PMS_uuid, parts[0][1:]))
            else:
                el = el.find(parts[0])
            attrib = parts[1]
        
        # check element and get attribute
        if attrib.startswith('#') and attrib[1:] in self.variables:  # internal variable
            res = self.variables[attrib[1:]]
            dfltd = False
        elif attrib.startswith('$'):  # setting
            res = g_ATVSettings.getSetting(self.ATV_udid, attrib[1:])
            dfltd = False
        elif attrib.startswith('%'):  # PMS property
            res = PlexAPI.getPMSProperty(self.ATV_udid, self.PMS_uuid, attrib[1:])
            dfltd = False
        elif attrib.startswith('^') and attrib[1:] in self.options:  # aTV property, http request options
            res = self.options[attrib[1:]]
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
        while len(tag)>0:
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
                convlist.append((unquote_plus(convstr[0]), unquote_plus(convstr[1])))
        
        dprint(__name__, 2, "CCmds_getConversion: {0},{1}", convlist, leftover)
        return [convlist, leftover]
    
    def applyConversion(self, val, convlist):
        # apply string conversion
	encodedval = val.replace(" ", "+")
        if convlist!=[]:
            for part in reversed(sorted(convlist)):
                if encodedval>=part[0]:
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
        cnt = 0
        for elemSRC in src.findall(tag):
            key = 'COPY'
            if param_enbl!='':
                key, leftover, dfltd = self.getKey(elemSRC, srcXML, param_enbl)
                conv, leftover = self.getConversion(elemSRC, leftover)
                if not dfltd:
                    key = self.applyConversion(key, conv)
            
            if key:
                self.PMSroot['copy_'+tag] = elemSRC
                self.variables['copy_ix'] = str(cnt)
                cnt = cnt+1
                el = copy.deepcopy(child)
                XML_ExpandTree(self, el, elemSRC, srcXML)
                XML_ExpandAllAttrib(self, el, elemSRC, srcXML)
                
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
    
    #syntax: Video, playType (Single|Continuous), key to match (^PlexConnectRatingKey), ratingKey
    def TREE_COPY_PLAYLIST(self, elem, child, src, srcXML, param):
        tag, leftover  = self.getParam(src, param)
        playType, leftover, dfltd = self.getKey(src, srcXML, leftover)  # Single (default), Continuous
        key, leftover, dfltd = self.getKey(src, srcXML, leftover)
        param_key = leftover
        
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
        
        # filter elements to copy
        cnt = 0
        copy_enbl = False
        elemsSRC = []
        for elemSRC in src.findall(tag):
            child_key, leftover, dfltd = self.getKey(elemSRC, srcXML, param_key)
            if not key:
                copy_enbl = True                           # copy all
            elif playType == 'Continuous' or playType== 'Shuffle':
                copy_enbl = copy_enbl or (key==child_key)  # [0 0 1 1 1 1]
            else:  # 'Single' (default)
                copy_enbl = (key==child_key)               # [0 0 1 0 0 0]
            
            if copy_enbl:
                elemsSRC.append(elemSRC)
        
        # shuffle elements
        if playType == 'Shuffle':
            if not key:
                random.shuffle(elemsSRC)                   # shuffle all
            else:
                elems = elemsSRC[1:]                       # keep first element fix
                random.shuffle(elems)
                elemsSRC = [elemsSRC[0]] + elems
        
        # duplicate child and add to tree
        cnt = 0
        for elemSRC in elemsSRC:
                self.PMSroot['copy_'+tag] = elemSRC
                self.variables['copy_ix'] = str(cnt)
                cnt = cnt+1
                el = copy.deepcopy(child)
                XML_ExpandTree(self, el, elemSRC, srcXML)
                XML_ExpandAllAttrib(self, el, elemSRC, srcXML)
                
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
        
        PMS_address = self.PMS_address
        
        if key.startswith('//'):  # local servers signature
            pathstart = key.find('/',3)
            PMS_address= key[:pathstart]
            path = key[pathstart:]
        elif key.startswith('/'):  # internal full path.
            path = key
        #elif key.startswith('http://'):  # external address
        #    path = key
        elif key == '':  # internal path
            path = self.path[srcXML]
        else:  # internal path, add-on
            path = self.path[srcXML] + '/' + key
        
        if PMS_address in ['all', 'owned', 'shared', 'local', 'remote']:
            # owned, shared PMSs
            type = PMS_address
            PMS = PlexAPI.getXMLFromMultiplePMS(self.ATV_udid, path, type, self.options)
        else:
            # IP:port or plex.tv
            auth_token = PlexAPI.getPMSProperty(self.ATV_udid, self.PMS_uuid, 'accesstoken')
            enableGzip = PlexAPI.getPMSProperty(self.ATV_udid, self.PMS_uuid, 'enableGzip')
            PMS = PlexAPI.getXMLFromPMS(self.PMS_baseURL, path, self.options, auth_token, enableGzip)
        
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
    
    def TREE_MEDIABADGES(self, elem, child, src, srcXML, param):
        resolution, leftover, dfltd = self.getKey(src, srcXML, param + "/videoResolution")
        container, leftover, dfltd = self.getKey(src, srcXML, param + "/container")
        vCodec, leftover, dfltd = self.getKey(src, srcXML, param + "/videoCodec")
        aCodec, leftover, dfltd = self.getKey(src, srcXML, param + "/audioCodec")
        channels, leftover, dfltd = self.getKey(src, srcXML, param + "/audioChannels")  
        
        additionalBadges = etree.Element("additionalMediaBadges")
        index = 0
        attribs = {'insertIndex': '0', 'required': 'true', 'src': ''}
        
        # Resolution
        if resolution not in ['720', '1080', '2k', '4k']:
            attribs['src'] = g_param['baseURL'] + '/thumbnails/MediaBadges/sd.png'
        else:
            attribs['src'] = g_param['baseURL'] + '/thumbnails/MediaBadges/' + resolution + '.png'
        urlBadge = etree.SubElement(additionalBadges, "urlBadge", attribs)
        index += 1
        # Special case iTunes DRM
        if vCodec == 'drmi' or aCodec == 'drms':
            attribs['insertIndex'] = str(index)
            attribs['src'] = g_param['baseURL'] + '/thumbnails/MediaBadges/iTunesDRM.png'
            urlBadge = etree.SubElement(additionalBadges, "urlBadge", attribs)
            child.append(additionalBadges)
            return True # Finish, no more info needed
        # File container
        if container != '' and self.options['aTVFirmwareVersion'] >= '7.0':
            attribs['insertIndex'] = str(index)
            attribs['src'] = g_param['baseURL'] + '/thumbnails/MediaBadges/' + container + '.png'
            urlBadge = etree.SubElement(additionalBadges, "urlBadge", attribs)
            index += 1
        # Video Codec
        if vCodec != '' and self.options['aTVFirmwareVersion'] >= '7.0':
            if vCodec == 'mpeg4':
                vCodec = 'xvid' # Are there any other mpeg4-part 2 codecs?
            attribs['insertIndex'] = str(index)
            attribs['src'] = g_param['baseURL'] + '/thumbnails/MediaBadges/' + vCodec + '.png'
            urlBadge = etree.SubElement(additionalBadges, "urlBadge", attribs)
            index += 1    
        # Audio Codec
        if aCodec != '':
            attribs['insertIndex'] = str(index)
            attribs['src'] = g_param['baseURL'] + '/thumbnails/MediaBadges/' + aCodec + '.png'
            urlBadge = etree.SubElement(additionalBadges, "urlBadge", attribs)
            index += 1 
        # Audio Channels
        if channels != '':
            attribs['insertIndex'] = str(index)
            attribs['src'] = g_param['baseURL'] + '/thumbnails/MediaBadges/' + channels + '.png'
            urlBadge = etree.SubElement(additionalBadges, "urlBadge", attribs)
        # Append XML
        child.append(additionalBadges)
        return True # Tree changed
        
            
    # XML ATTRIB modifier commands
    # add new commands to this list!
    def ATTRIB_VAL(self, src, srcXML, param):
        key, leftover, dfltd = self.getKey(src, srcXML, param)
        conv, leftover = self.getConversion(src, leftover)
        if not dfltd:
            key = self.applyConversion(key, conv)
        return key
    
    def ATTRIB_EVAL(self, src, srcXML, param):
        return str(eval(param))

    def ATTRIB_VAL_QUOTED(self, src, srcXML, param):
        key, leftover, dfltd = self.getKey(src, srcXML, param)
        conv, leftover = self.getConversion(src, leftover)
        if not dfltd:
            key = self.applyConversion(key, conv)
        return quote_plus(unicode(key).encode("utf-8"))

    def ATTRIB_SETTING(self, src, srcXML, param):
        opt, leftover = self.getParam(src, param)
        return g_ATVSettings.getSetting(self.ATV_udid, opt)
    
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
        
        PMS_uuid = self.PMS_uuid
        PMS_baseURL = self.PMS_baseURL
        cmd_start = key.find('PMS(')
        cmd_end = key.find(')', cmd_start)
        if cmd_start>-1 and cmd_end>-1 and cmd_end>cmd_start:
            PMS_address = key[cmd_start+4:cmd_end]
            PMS_uuid = PlexAPI.getPMSFromAddress(self.ATV_udid, PMS_address)
            PMS_baseURL = PlexAPI.getPMSProperty(self.ATV_udid, PMS_uuid, 'baseURL')
            key = key[cmd_end+1:]
        
        AuthToken = PlexAPI.getPMSProperty(self.ATV_udid, PMS_uuid, 'accesstoken')
        
        # transcoder action
        transcoderAction = g_ATVSettings.getSetting(self.ATV_udid, 'phototranscoderaction')
        
        # image orientation
	orientation, leftover, dfltd = self.getKey(src, srcXML, 'Media/Part/orientation')
	normalOrientation = (not orientation) or orientation=='1'
        
        # aTV native filetypes
        parts = key.rsplit('.',1)
        photoATVNative = parts[-1].lower() in ['jpg','jpeg','tif','tiff','gif','png']
        dprint(__name__, 2, "photo: ATVNative - {0}", photoATVNative)
        
        if width=='' and \
           transcoderAction=='Auto' and \
           normalOrientation and \
           photoATVNative:
            # direct play
            res = PlexAPI.getDirectImagePath(key, AuthToken)
        else:
            if width=='':
                width = 1920  # max for HDTV. Relate to aTV version? Increase for KenBurns effect?
            if height=='':
                height = 1080  # as above
            # request transcoding
            res = PlexAPI.getTranscodeImagePath(key, AuthToken, self.path[srcXML], width, height)
        
        if res.startswith('/'):  # internal full path.
            res = PMS_baseURL + res
        elif res.startswith('http://') or key.startswith('https://'):  # external address
            pass
        else:  # internal path, add-on
            res = PMS_baseURL + self.path[srcXML] + '/' + res
        
        dprint(__name__, 1, 'ImageURL: {0}', res)
        return res
    
    def ATTRIB_MUSICURL(self, src, srcXML, param):
        Track, leftover = self.getElement(src, srcXML, param)
        
        AuthToken = PlexAPI.getPMSProperty(self.ATV_udid, self.PMS_uuid, 'accesstoken')
        
        if not Track:
            # not a complete audio/track structure - take key directly and build direct-play path
            key, leftover, dfltd = self.getKey(src, srcXML, param)
            res = PlexAPI.getDirectAudioPath(key, AuthToken)
            res = PlexAPI.getURL(self.PMS_baseURL, self.path[srcXML], res)
            dprint(__name__, 1, 'MusicURL - direct: {0}', res)
            return res
        
        # complete track structure - request transcoding if needed
        Media = Track.find('Media')
        
        # check "Media" element and get key
        if Media!=None:
            # transcoder action setting?
            # transcoder bitrate setting [kbps] -  eg. 128, 256, 384, 512?
            maxAudioBitrateCompressed = '320'
                        
            audioATVNative = \
                Media.get('audioCodec','-') in ("mp3", "aac", "ac3", "drms") and \
                int(Media.get('bitrate','0')) <= int(maxAudioBitrateCompressed) \
                or \
                Media.get('audioCodec','-') in ("alac", "aiff", "wav")
            # check Media.get('container') as well - mp3, m4a, ...?
            
            dprint(__name__, 2, "audio: ATVNative - {0}", audioATVNative)
            
            if audioATVNative:
                # direct play
                res, leftover, dfltd = self.getKey(Media, srcXML, 'Part/key')
                res = PlexAPI.getDirectAudioPath(res, AuthToken)
            else:
                # request transcoding
                res, leftover, dfltd = self.getKey(Track, srcXML, 'key')
                res = PlexAPI.getTranscodeAudioPath(res, AuthToken, self.options, maxAudioBitrateCompressed)
        
        else:
            dprint(__name__, 0, "MEDIAPATH - element not found: {0}", param)
            res = 'FILE_NOT_FOUND'  # not found?
        
        res = PlexAPI.getURL(self.PMS_baseURL, self.path[srcXML], res)
        dprint(__name__, 1, 'MusicURL: {0}', res)
        return res
    
    def ATTRIB_URL(self, src, srcXML, param):
        key, leftover, dfltd = self.getKey(src, srcXML, param)
        addPath, leftover = self.getParam(src, leftover)
        addOpt, leftover = self.getParam(src, leftover)
        
        # compare PMS_mark in PlexAPI/getXMLFromMultiplePMS()
        PMS_mark = '/PMS(' + self.PMS_address + ')'
        
        # overwrite with URL embedded PMS address
        cmd_start = key.find('PMS(')
        cmd_end = key.find(')', cmd_start)
        if cmd_start>-1 and cmd_end>-1 and cmd_end>cmd_start:
            PMS_mark = '/'+key[cmd_start:cmd_end+1]
            key = key[cmd_end+1:]
        
        res = g_param['baseURL']  # base address to PlexConnect
        
        if key.endswith('.js'):  # link to PlexConnect owned .js stuff
            res = res + key
        elif key.startswith('http://') or key.startswith('https://'):  # external server
            res = key
            """
            parts = urlparse.urlsplit(key)  # (scheme, networklocation, path, ...)
            key = urlparse.urlunsplit(('', '', parts[2], parts[3], parts[4]))  # keep path only
            PMS_uuid = PlexAPI.getPMSFromIP(g_param['PMS_list'], parts.hostname)
            PMSaddress = PlexAPI.getAddress(g_param['PMS_list'], PMS_uuid)  # get PMS address (might be local as well!?!)
            res = res + '/PMS(' + quote_plus(PMSaddress) + ')' + key
            """
        elif key.startswith('/'):  # internal full path.
            res = res + PMS_mark + key
        elif key == '':  # internal path
            res = res + PMS_mark + self.path[srcXML]
        else:  # internal path, add-on
            res = res + PMS_mark + self.path[srcXML] + '/' + key
        
        if addPath:
            res = res + addPath
        
        if addOpt:
            if not '?' in res:
                res = res +'?'+ addOpt
            else:
                res = res +'&'+ addOpt
        
        return res
    
    def ATTRIB_VIDEOURL(self, src, srcXML, param):
        Video, leftover = self.getElement(src, srcXML, param)
        partIndex, leftover, dfltd = self.getKey(src, srcXML, leftover)
        partIndex = int(partIndex) if partIndex else 0
        
        AuthToken = PlexAPI.getPMSProperty(self.ATV_udid, self.PMS_uuid, 'accesstoken')
        
        if not Video:
            dprint(__name__, 0, "VIDEOURL - VIDEO element not found: {0}", param)
            res = 'VIDEO_ELEMENT_NOT_FOUND'  # not found?
            return res
        
        # complete video structure - request transcoding if needed
        Media = Video.find('Media')
        
        # check "Media" element and get key
        if Media!=None:
            # transcoder action
            transcoderAction = g_ATVSettings.getSetting(self.ATV_udid, 'transcoderaction')
	    # transcoderAction = "Transcode"
            
            # video format
            #    HTTP live stream
            # or native aTV media
            videoATVNative = \
                Media.get('protocol','-') in ("hls") \
                or \
                Media.get('container','-') in ("mov", "mp4") and \
                Media.get('videoCodec','-') in ("mpeg4", "h264", "drmi") and \
                Media.get('audioCodec','-') in ("aac", "drms")   # remove AC3 when Dolby Digital is Off

	    # determine if Dolby Digital is active
	    DolbyDigital = g_ATVSettings.getSetting(self.ATV_udid, 'dolbydigital')
	    if DolbyDigital=='On':
		self.options['DolbyDigital'] = True
                videoATVNative = \
                    Media.get('protocol','-') in ("hls") \
                    or \
                    Media.get('container','-') in ("mov", "mp4") and \
                    Media.get('videoCodec','-') in ("mpeg4", "h264", "drmi") and \
                    Media.get('audioCodec','-') in ("aac", "ac3", "drms")
            
            for Stream in Media.find('Part').findall('Stream'):
                if Stream.get('streamType','') == '1' and\
                   Stream.get('codec','-') in ("mpeg4", "h264"):
                    if Stream.get('profile', '-') == 'high 10' or \
                        int(Stream.get('refFrames','0')) > 8:
                            videoATVNative = False
                            break
                if Stream.get('scanType', '') == 'interlaced' or Stream.get('codec') == 'mpeg2video':
                    videoATVNative = False
                    break
            
            dprint(__name__, 2, "video: ATVNative - {0}", videoATVNative)
            
            # quality limits: quality=(resolution, quality, bitrate)
            qLookup = { '480p 2.0Mbps' :('720x480', '60', '2000'), \
                        '720p 3.0Mbps' :('1280x720', '75', '3000'), \
                        '720p 4.0Mbps' :('1280x720', '100', '4000'), \
                        '1080p 8.0Mbps' :('1920x1080', '60', '8000'), \
                        '1080p 10.0Mbps' :('1920x1080', '75', '10000'), \
                        '1080p 12.0Mbps' :('1920x1080', '90', '12000'), \
                        '1080p 20.0Mbps' :('1920x1080', '100', '20000'), \
                        '1080p 40.0Mbps' :('1920x1080', '100', '40000') }
            if PlexAPI.getPMSProperty(self.ATV_udid, self.PMS_uuid, 'local')=='1':
                qLimits = qLookup[g_ATVSettings.getSetting(self.ATV_udid, 'transcodequality')]
            else:
                qLimits = qLookup[g_ATVSettings.getSetting(self.ATV_udid, 'remotebitrate')]
            
            # subtitle renderer, subtitle selection
            subtitleRenderer = g_ATVSettings.getSetting(self.ATV_udid, 'subtitlerenderer')
            
            subtitleId = ''
            subtitleKey = ''
            subtitleCodec = ''
            for Stream in Media.find('Part').findall('Stream'):  # Todo: check 'Part' existance, deal with multi part video
                if Stream.get('streamType','') == '3' and\
                   Stream.get('selected','0') == '1':
                    subtitleId = Stream.get('id','')
                    subtitleKey = Stream.get('key','')
                    subtitleCodec = Stream.get('codec','')
                    break
            
            subtitleIOSNative = \
                subtitleKey=='' and (subtitleCodec=="mov_text" or subtitleCodec=="ttxt" or subtitleCodec=="tx3g" or subtitleCodec=="text")  # embedded
            subtitlePlexConnect = \
                subtitleKey!='' and subtitleCodec=="srt"  # external
            
            # subtitle suitable for direct play?
            #    no subtitle
            # or 'Auto'    with subtitle by iOS or PlexConnect
            # or 'iOS,PMS' with subtitle by iOS
            subtitleDirectPlay = \
                subtitleId=='' \
                or \
                subtitleRenderer=='Auto' and \
                ( (videoATVNative and subtitleIOSNative) or subtitlePlexConnect ) \
                or \
                subtitleRenderer=='iOS, PMS' and \
                (videoATVNative and subtitleIOSNative)
            dprint(__name__, 2, "subtitle: IOSNative - {0}, PlexConnect - {1}, DirectPlay - {2}", subtitleIOSNative, subtitlePlexConnect, subtitleDirectPlay)
            
            # determine video URL
            if transcoderAction=='DirectPlay' \
               or \
               transcoderAction=='Auto' and \
               videoATVNative and \
               int(Media.get('bitrate','0')) < int(qLimits[2]) and \
               subtitleDirectPlay:
                # direct play for...
                #    force direct play
                # or videoATVNative (HTTP live stream m4v/h264/aac...)
                #    limited by quality setting
                #    with aTV supported subtitle (iOS embedded tx3g, PlexConnext external srt)
                res, leftover, dfltd = self.getKey(Media, srcXML, 'Part['+str(partIndex+1)+']/key')
                
                if Media.get('indirect', False):  # indirect... todo: select suitable resolution, today we just take first Media
                    PMS = PlexAPI.getXMLFromPMS(self.PMS_baseURL, res, self.options, AuthToken)  # todo... check key for trailing '/' or even 'http'
                    res, leftover, dfltd = self.getKey(PMS.getroot(), srcXML, 'Video/Media/Part['+str(partIndex+1)+']/key')
                
                res = PlexAPI.getDirectVideoPath(res, AuthToken)
            else:
                # request transcoding
                res = Video.get('key','')
                
                # misc settings: subtitlesize, audioboost
                subtitle = { 'selected': '1' if subtitleId else '0', \
                             'dontBurnIn': '1' if subtitleDirectPlay else '0', \
                             'size': g_ATVSettings.getSetting(self.ATV_udid, 'subtitlesize') }
                audio = { 'boost': g_ATVSettings.getSetting(self.ATV_udid, 'audioboost') }
                res = PlexAPI.getTranscodeVideoPath(res, AuthToken, self.options, transcoderAction, qLimits, subtitle, audio, partIndex)
        
        else:
            dprint(__name__, 0, "VIDEOURL - MEDIA element not found: {0}", param)
            res = 'MEDIA_ELEMENT_NOT_FOUND'  # not found?
        
        if res.startswith('/'):  # internal full path.
            res = self.PMS_baseURL + res
        elif res.startswith('http://') or res.startswith('https://'):  # external address
            pass
        else:  # internal path, add-on
            res = self.PMS_baseURL + self.path[srcXML] + res
        
        dprint(__name__, 1, 'VideoURL: {0}', res)
        return res
    
    def ATTRIB_episodestring(self, src, srcXML, param):
        parentIndex, leftover, dfltd = self.getKey(src, srcXML, param)  # getKey "defaults" if nothing found.
        index, leftover, dfltd = self.getKey(src, srcXML, leftover)
        title, leftover, dfltd = self.getKey(src, srcXML, leftover)
        out = self._("{0:0d}x{1:02d} {2}").format(int(parentIndex), int(index), title)
        return out

    def ATTRIB_durationToString(self, src, srcXML, param):
        type, leftover, dfltd = self.getKey(src, srcXML, param)
        duration, leftover, dfltd = self.getKey(src, srcXML, leftover)
        if type == 'Video':
            min = int(duration)/1000/60
            if g_ATVSettings.getSetting(self.ATV_udid, 'durationformat') == 'Minutes':
                return self._("{0:d} Minutes").format(min)
            else:
                if len(duration) > 0:
                    hour = min/60
                    min = min%60
                    if hour == 0: return self._("{0:d} Minutes").format(min)
                    else: return self._("{0:d}hr {1:d}min").format(hour, min)
        
        if type == 'Audio':
            secs = int(duration)/1000
            if len(duration) > 0:
                mins = secs/60
                secs = secs%60
                return self._("{0:d}:{1:0>2d}").format(mins, secs)
        
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
        return str(PlexAPI.getPMSCount(self.ATV_udid) - 1)  # -1: correct for plex.tv
    
    def ATTRIB_PMSNAME(self, src, srcXML, param):
        PMS_name = PlexAPI.getPMSProperty(self.ATV_udid, self.PMS_uuid, 'name')
        if PMS_name=='':
            return "No Server in Proximity"
        else:
            return PMS_name
    
    def ATTRIB_BACKGROUNDURL(self, src, srcXML, param):
        key, leftover, dfltd = self.getKey(src, srcXML, param)
        
        if key.startswith('/'):  # internal full path.
            key = self.PMS_baseURL + key
        elif key.startswith('http://') or key.startswith('https://'):  # external address
            pass
        else:  # internal path, add-on
            key = self.PMS_baseURL + self.path[srcXML] + key
        
        auth_token = PlexAPI.getPMSProperty(self.ATV_udid, self.PMS_uuid, 'accesstoken')
        
        dprint(__name__, 1, "Background (Source): {0}", key)
        res = g_param['baseURL']  # base address to PlexConnect
        res = res + PILBackgrounds.generate(self.PMS_uuid, key, auth_token, self.options['aTVScreenResolution'], g_ATVSettings.getSetting(self.ATV_udid, 'fanart_blur'), g_param['CSettings'])
        dprint(__name__, 1, "Background: {0}", res)
        return res



if __name__=="__main__":
    cfg = Settings.CSettings()
    param = {}
    param['CSettings'] = cfg

    param['HostToIntercept'] = cfg.getSetting('hosttointercept')
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
    print prettyXML(PMSroot)
    
    print
    print "load aTV XML template"
    _XML = '<aTV> \
                <INFO num="{{VAL(number)}}" str="{{VAL(string)}}">Info</INFO> \
                <FILE str="{{VAL(string)}}" strconv="{{VAL(string::World=big|Moon=small|Sun=huge)}}" num="{{VAL(number:5)}}" numfunc="{{EVAL(int({{VAL(number:5)}}/10))}}"> \
                    File{{COPY(DATA)}} \
                </FILE> \
                <PATH path="{{ADDPATH(file:unknown)}}" /> \
                <accessories> \
                    <cut />{{CUT(number::0=cut|1=)}} \
                    <dontcut />{{CUT(attribnotfound)}} \
                </accessories> \
                <ADDPATH>{{ADDPATH(string)}}</ADDPATH> \
                <COPY2>={{COPY(DATA)}}=</COPY2> \
            </aTV>'
    aTVroot = etree.fromstring(_XML)
    aTVTree = etree.ElementTree(aTVroot)
    print prettyXML(aTVroot)
    
    print
    print "unpack PlexConnect COPY/CUT commands"
    options = {}
    options['PlexConnectUDID'] = '007'
    PMS_address = 'PMS_IP'
    CommandCollection = CCommandCollection(options, PMSroot, PMS_address, '/library/sections')
    XML_ExpandTree(CommandCollection, aTVroot, PMSroot, 'main')
    XML_ExpandAllAttrib(CommandCollection, aTVroot, PMSroot, 'main')
    del CommandCollection
    
    print
    print "resulting aTV XML"
    print prettyXML(aTVroot)
    
    print
    #print "store aTV XML"
    #str = prettyXML(aTVTree)
    #f=open(sys.path[0]+'/XML/aTV_fromTmpl.xml', 'w')
    #f.write(str)
    #f.close()
    
    del cfg
