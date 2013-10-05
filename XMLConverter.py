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

PlexAPI_getTranscodePath() based on getTranscodeURL from pyplex/plexAPI
https://github.com/megawubs/pyplex/blob/master/plexAPI/info.py

Basic Authentication:
http://www.voidspace.org.uk/python/articles/urllib2.shtml
http://www.voidspace.org.uk/python/articles/authentication.shtml
http://stackoverflow.com/questions/2407126/python-urllib2-basic-auth-problem
http://stackoverflow.com/questions/111945/is-there-any-way-to-do-http-put-in-python
(and others...)
"""


import os
import sys
import traceback
import inspect
import string, cgi, time
import copy  # deepcopy()
from os import sep
import httplib, socket
<<<<<<< HEAD
import re
from ast import literal_eval
||||||| merged common ancestors

=======
import urllib2

>>>>>>> c0ccb7ea5564d55982b6e5881405e00807d28350


try:
    import xml.etree.cElementTree as etree
except ImportError:
    import xml.etree.ElementTree as etree

import time, uuid, hmac, hashlib, base64
from urllib import urlencode
from urlparse import urlparse
from urllib import quote_plus
from urllib import FancyURLopener

import Settings, ATVSettings
import PlexGDM
from Debug import *  # dprint()
import Localize
from PlexMgr import *


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



def XML_PlayVideo_ChannelsV1(path):
    XML = '\
<atv>\n\
  <body>\n\
    <videoPlayer id="com.sample.video-player">\n\
      <httpFileVideoAsset id="' + path + '">\n\
        <mediaURL>http://' + g_param['Addr_PMS'] +  path + '</mediaURL>\n\
        <title>*title*</title>\n\
        <!--bookmarkTime>{{EVAL(Video/viewOffset:0:int(x/1000))}}</bookmarkTime-->\n\
      </httpFileVideoAsset>\n\
    </videoPlayer>\n\
  </body>\n\
</atv>\n\
';
    dprint(__name__,2 , XML)
    return XML



"""
# GetURL
# Source (somewhat): https://github.com/hippojay/plugin.video.plexbmc
"""
def GetURL(address, path, authToken):
    try:
        conn = httplib.HTTPConnection(address, timeout=10)

        headers = {}

        if authToken!="":
            headers = {'X-Plex-Token' : authToken}

        conn.request("GET", path, None, headers)

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
def XML_ReadFromURL(address, path, authToken):
    xargs = PlexAPI_getXArgs()
    if path.find('?')>=0:
        path = path + '&' + urlencode(xargs)
    else:
        path = path + '?' + urlencode(xargs)

    XMLstring = GetURL(address, path, authToken)
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


def XML_PMS2aTV(address, path, options):

    cmd = ''
    if 'PlexConnect' in options:
        cmd = options['PlexConnect']
    dprint(__name__, 1, "PlexConnect Cmd: "+cmd)

    if not 'PlexConnectUDID' in options:
        dprint(__name__, 1, "no PlexConnectUDID - pick 007")
        options['PlexConnectUDID'] = '007'

    if not 'aTVLanguage' in options:
        dprint(__name__, 1, "no aTVLanguage - pick en")
        options['aTVLanguage'] = 'en'

    #Create a Plex Manager.
    #Create it from state - if a .p file exists for this UDID, it will depickle and restore the state, otherwise, it just creates a new one.
    if options['PlexConnectUDID'] not in options['PlexMgr']:
        options['PlexMgr'][options['PlexConnectUDID']] = CPlexMgr(options['PlexConnectUDID'], g_ATVSettings)
    #PlexMgr = CPlexMgr.from_state(options['PlexConnectUDID'])
    PlexMgr = options['PlexMgr'][options['PlexConnectUDID']]

    if path=="/library/sections":
        enableGDM = g_param['CSettings'].getSetting('enable_plexgdm')
        if enableGDM=='True':
            rediscover = PlexMgr.discoverPMS(False)
        else:
            rediscover = PlexMgr.discoverPMS(False, g_param['CSettings'].getSetting('ip_pms'), g_param['CSettings'].getSetting('port_pms'))

        g_ATVSettings.setOptions('pms_uuid', PlexMgr.getLocalServerNames())

        if PlexMgr.myPlexLoggedIn()==True:
            PlexMgr.discovermyPlex()


    if path=="/library/sections" or path=="/PlexConnect.xml" or path=="/channels/all":
        PlexMgr.currentServer = "Preferred" #Pretty much any initial startup/channels should be preferred local server.

    if path.startswith("/passthru"):
        #let PlexMgr know about the request to change servers.
        PlexMgr.currentServer = re.findall(r'URL=http://([a-z0-9\.:]+)[^&?]+', path)[0]

        #If it's a local request, pass it to the preferred server.
        if PlexMgr.currentServer=="atv.plexconnect":
            PlexMgr.currentServer = "Preferred"

        #and just pass the path through
        path = re.findall(r'URL=http://[a-z0-9\.:]+([^&?]+)', path)[0]


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
        return XML_PlayVideo_ChannelsV1(path)  # direct link, no PMS XML available

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

    elif cmd=='Channels':
        XMLtemplate = 'Channels.xml'

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

    elif cmd=='SettingsMyPlex':
        XMLtemplate = 'Settings_MyPlex.xml'
        path = ''  # clear path - we don't need PMS-XML

    elif cmd.startswith('LoginMyPlex:'):
        opt = cmd[len('LoginMyPlex:'):]  # cut command:
        parts = opt.split('+')
        dprint(__name__, 2, "MyPlex->Checking Service...")
        PlexMgr.myPlexLogin(parts[0], parts[1])

        if PlexMgr.myPlexLoggedIn()==False:
            #I don't know if I should bother keeping this state.. I'll do it for now.
            g_ATVSettings.setSetting(options['PlexConnectUDID'], "myplexuser", "")
            g_ATVSettings.setSetting(options['PlexConnectUDID'], "myplex_uuid", "")
            XMLtemplate = 'MyPlexAuthError.xml'
            path = ''
        else:
            g_ATVSettings.setSetting(options['PlexConnectUDID'], "myplexuser", parts[0])
            g_ATVSettings.setSetting(options['PlexConnectUDID'], "myplex_uuid", PlexMgr.myplex_token)
            XMLtemplate = 'MyPlexAuthOK.xml'
            path = ''

    elif cmd.startswith('LogoutMyPlex'):
        dprint(__name__, 2, "MyPlex->Logging Out...")
        PlexMgr.myPlexLogout()
        g_ATVSettings.setSetting(options['PlexConnectUDID'], "myplexuser", "")
        g_ATVSettings.setSetting(options['PlexConnectUDID'], "myplex_uuid", "")
        XMLtemplate = 'MyPlexLogout.xml'
        path = ''

    elif cmd.startswith('SettingsToggle:'):
        opt = cmd[len('SettingsToggle:'):]  # cut command:
        parts = opt.split('+')
        g_ATVSettings.toggleSetting(options['PlexConnectUDID'], parts[0].lower())
        XMLtemplate = parts[1] + ".xml"
        dprint(__name__, 2, "ATVSettings->Toggle: {0} in template: {1}", parts[0], parts[1])

        path = ''  # clear path - we don't need PMS-XML
<<<<<<< HEAD

||||||| merged common ancestors
    
=======
        
    elif cmd==('MyPlexLogin'):
        dprint(__name__, 2, "MyPlex->Logging In...")
        if not 'PlexConnectCredentials' in options:
            return XML_Error('PlexConnect', 'MyPlex Sign In called without Credentials.')
        
        parts = options['PlexConnectCredentials'].split(':',1)        
        (username, auth_token) = PlexAPI_MyPlexSignIn(parts[0], parts[1], options['PlexConnectUDID'])
        
        UDID = options['PlexConnectUDID']
        g_ATVSettings.setSetting(UDID, 'myplex_user', username)
        g_ATVSettings.setSetting(UDID, 'myplex_auth', auth_token)
        
        XMLtemplate = 'Settings.xml'
        path = ''  # clear path - we don't need PMS-XML
    
    elif cmd=='MyPlexLogout':
        dprint(__name__, 2, "MyPlex->Logging Out...")
        
        UDID = options['PlexConnectUDID']
        auth_token = g_ATVSettings.getSetting(UDID, 'myplex_auth')
        PlexAPI_MyPlexSignOut(auth_token)
        
        g_ATVSettings.setSetting(UDID, 'myplex_user', '')
        g_ATVSettings.setSetting(UDID, 'myplex_auth', '')
        
        XMLtemplate = 'Settings.xml'
        path = ''  # clear path - we don't need PMS-XML
    
>>>>>>> c0ccb7ea5564d55982b6e5881405e00807d28350
    elif cmd.startswith('Discover'):
        #Force Discovery.
        enableGDM = g_param['CSettings'].getSetting('enable_plexgdm')
        if enableGDM=='True':
            rediscover = PlexMgr.discoverPMS(True)
        else:
            rediscover = PlexMgr.discoverPMS(True, g_param['CSettings'].getSetting('ip_pms'), g_param['CSettings'].getSetting('port_pms'))

        g_ATVSettings.setOptions('pms_uuid', PlexMgr.getLocalServerNames())

        if PlexMgr.myPlexLoggedIn()==True:
            PlexMgr.discovermyPlex(True)


        XMLtemplate = 'Settings.xml'
        path = ''  # clear path - we don't need PMS-XML

    elif path.startswith('/search?'):
        XMLtemplate = 'Search_Results.xml'

    #preferred uuid:
    PMS_uuid = g_ATVSettings.getSetting(options['PlexConnectUDID'], 'pms_uuid')
    enableGDM = g_param['CSettings'].getSetting('enable_plexgdm')

    if PlexMgr.currentServer=="Preferred":
        #This will force Plex to use the default local server.


        # we need PMS but don't see selected one: re-discover (PlexGDM)
        if not path=='' and PlexMgr.getServerByUUID(PMS_uuid)==None:
            if enableGDM=='True':
                rediscover = PlexMgr.discoverPMS(True)
            else:
                rediscover = PlexMgr.discoverPMS(True, g_param['CSettings'].getSetting('ip_pms'), g_param['CSettings'].getSetting('port_pms'))

            g_ATVSettings.setOptions('pms_uuid', PlexMgr.getLocalServerNames())
            if not rediscover:
                return XML_Error('PlexConnect', 'No Plex Media Server in Proximity')
            g_ATVSettings.checkSetting(options['PlexConnectUDID'], 'pms_uuid')  # verify PMS_uuid
            PMS_uuid = g_ATVSettings.getSetting(options['PlexConnectUDID'], 'pms_uuid')

        # determine PMS IP address
        if PlexMgr.getServerByUUID(PMS_uuid)!=None:
            pSrv = PlexMgr.getServerByUUID(PMS_uuid)
            g_param['Addr_PMS'] = pSrv.address +':'+ pSrv.port


    else:
        g_param['Addr_PMS'] = PlexMgr.currentServer


    # request PMS XML
    if not path=='':
        if len(PlexMgr.servers)==0:
            # PlexGDM
            if not PlexMgr.discoverPMS(True):
                return XML_Error('PlexConnect', 'No Plex Media Server in Proximity')

        if PlexMgr.getServerByUUID(PMS_uuid)==None:
            return XML_Error('PlexConnect', 'Selected Plex Media Server not Online')

        PMS = XML_ReadFromURL(g_param['Addr_PMS'], path, PlexMgr.getTokenFromAddress(g_param['Addr_PMS']))
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
        if PlexMgr.myPlexLoggedIn()!=True:
            XMLtemplate = 'Directory.xml'
        else:
            XMLtemplate = 'DirectoryMyPlex.xml'

    dprint(__name__, 1, "XMLTemplate: "+XMLtemplate)

    # get XMLtemplate
    aTVTree = etree.parse(sys.path[0]+'/assets/templates/'+XMLtemplate)
    aTVroot = aTVTree.getroot()

    # convert PMS XML to aTV XML using provided XMLtemplate
    global g_CommandCollection
    g_CommandCollection = CCommandCollection(options, PMSroot, path)
    XML_ExpandTree(aTVroot, PMSroot, 'main')
    XML_ExpandAllAttrib(aTVroot, PMSroot, 'main')
    del g_CommandCollection

    PMS = etree.ElementTree(PMSroot)

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
# PlexAPI
"""
def PlexAPI_getTranscodePath(options, path):
    UDID = options['PlexConnectUDID']
    transcodePath = '/video/:/transcode/universal/start.m3u8?'

    quality = { '480p 2.0Mbps' :('720x480', '60', '2000'), \
                '720p 3.0Mbps' :('1280x720', '75', '3000'), \
                '720p 4.0Mbps' :('1280x720', '100', '4000'), \
                '1080p 8.0Mbps' :('1920x1080', '60', '8000'), \
                '1080p 10.0Mbps' :('1920x1080', '75', '10000'), \
                '1080p 12.0Mbps' :('1920x1080', '90', '12000'), \
                '1080p 20.0Mbps' :('1920x1080', '100', '20000'), \
                '1080p 40.0Mbps' :('1920x1080', '100', '40000') }
    setAction = g_ATVSettings.getSetting(UDID, 'transcoderaction')
    setQuality = g_ATVSettings.getSetting(UDID, 'transcodequality')
    vRes = quality[setQuality][0]
    vQ = quality[setQuality][1]
    mVB = quality[setQuality][2]
    dprint(__name__, 1, "Setting transcode quality Res:{0} Q:{1} {2}Mbps", vRes, vQ, mVB)
    sS = g_ATVSettings.getSetting(UDID, 'subtitlesize')
    dprint(__name__, 1, "Subtitle size: {0}", sS)
    aB = g_ATVSettings.getSetting(UDID, 'audioboost')
    dprint(__name__, 1, "Audio Boost: {0}", aB)

    args = dict()
    args['session'] = UDID
    args['protocol'] = 'hls'
    args['videoResolution'] = vRes
    args['maxVideoBitrate'] = mVB
    args['videoQuality'] = vQ
    args['directStream'] = '0' if setAction=='Transcode' else '1'
    # 'directPlay' - handled by the client in MEDIARUL()
    args['subtitleSize'] = sS
    args['audioBoost'] = aB
    args['fastSeek'] = '1'
    args['path'] = path

    xargs = PlexAPI_getXArgs(options)

    return transcodePath + urlencode(args) + '&' + urlencode(xargs)

def PlexAPI_getXArgs(options=None):
    xargs = dict()
    xargs['X-Plex-Device'] = 'AppleTV'
    xargs['X-Plex-Model'] = '3,1' # Base it on AppleTV model.
    if not options is None:
        if 'PlexConnectATVName' in options:
            xargs['X-Plex-Device-Name'] = options['PlexConnectATVName'] # "friendly" name: aTV-Settings->General->Name.
    xargs['X-Plex-Platform'] = 'iOS'
    xargs['X-Plex-Client-Platform'] = 'iOS'
    xargs['X-Plex-Platform-Version'] = '5.3' # Base it on AppleTV OS version.
    xargs['X-Plex-Product'] = 'PlexConnect'
    xargs['X-Plex-Version'] = '0.2'

    xargs['X-Plex-Client-Capabilities'] = "protocols=http-live-streaming,http-mp4-streaming,http-streaming-video,http-streaming-video-720p,http-mp4-video,http-mp4-video-720p;videoDecoders=h264{profile:high&resolution:1080&level:41};audioDecoders=mp3,aac{bitrate:160000}"

    return xargs



def PlexAPI_MyPlexSignIn(username, password, UDID):
    # MyPlex web address
    MyPlexHost = 'my.plexapp.com'
    MyPlexSignInPath = '/users/sign_in.xml'
    MyPlexURL = 'https://' + MyPlexHost + MyPlexSignInPath
    
    # create POST request
    request = urllib2.Request(MyPlexURL)
    request.add_header('X-Plex-Client-Identifier', UDID)  # xarg needed for MyPlex device identification
    request.get_method = lambda: 'POST'  # turn into 'POST' - done automatically with data!=None. But we don't have data.
    
    # no certificate, will fail with "401 - Authentification required"
    """
    try:
        f = urllib2.urlopen(request)
    except urllib2.HTTPError, e:
        print e.headers
        print "has WWW_Authenticate:", e.headers.has_key('WWW-Authenticate')
        print
    """
    
    # provide credentials
    ### optional... when 'realm' is unknown
    ##passmanager = urllib2.HTTPPasswordMgrWithDefaultRealm()
    ##passmanager.add_password(None, address, username, password)  # None: default "realm"
    passmanager = urllib2.HTTPPasswordMgr()
    passmanager.add_password(MyPlexHost, MyPlexURL, username, password)  # realm = 'my.plexapp.com'
    authhandler = urllib2.HTTPBasicAuthHandler(passmanager)
    urlopener = urllib2.build_opener(authhandler)
    
    # sign in, get MyPlex response
    try:
        f = urlopener.open(request)
        response = f.read()
    except urllib2.HTTPError, e:
        if e.code==401:
            dprint(__name__, 0, 'Authentication failed')
            return ('', '')
        else:
            raise
    
    dprint(__name__, 1, "====== MyPlex sign in XML ======")
    dprint(__name__, 1, response)
    dprint(__name__, 1, "====== MyPlex sign in XML finished ======")
    
    # analyse response
    XMLTree = etree.ElementTree(etree.fromstring(response))
    
    username = ''
    authtoken = ''
    el_username = XMLTree.find('username')
    el_authtoken = XMLTree.find('authentication-token')    
    if not el_username is None and \
       not el_authtoken is None:
        username = el_username.text
        authtoken = el_authtoken.text
    
    return (username, authtoken)

def PlexAPI_MyPlexSignOut(authtoken):
    # MyPlex web address
    MyPlexHost = 'my.plexapp.com'
    MyPlexSignOutPath = '/users/sign_out.xml'
    MyPlexURL = 'http://' + MyPlexHost + MyPlexSignOutPath
    
    # create POST request
    request = urllib2.Request(MyPlexURL)
    request.add_header('X-Plex-Token', authtoken)
    request.get_method = lambda: 'POST'  # turn into 'POST' - done automatically with data!=None. But we don't have data.
    
    response = urllib2.urlopen(request).read()
    
    dprint(__name__, 1, "====== MyPlex sign out XML ======")
    dprint(__name__, 1, response)
    dprint(__name__, 1, "====== MyPlex sign out XML finished ======")



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
    def __init__(self, options, PMSroot, path):
        self.options = options
        self.PMSroot = {'main': PMSroot}
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

        UDID = self.options['PlexConnectUDID']
        # walk the path if neccessary
        while '/' in attrib and el!=None:
            parts = attrib.split('/',1)
            if parts[0].startswith('#'):  # internal variable in path
                el = el.find(self.variables[parts[0][1:]])
            elif parts[0].startswith('$'):  # setting
                el = el.find(g_ATVSettings.getSetting(UDID, parts[0][1:]))
            else:
                el = el.find(parts[0])
            attrib = parts[1]

        # check element and get attribute
        if attrib.startswith('#'):  # internal variable
            res = self.variables[attrib[1:]]
            dfltd = False
        elif attrib.startswith('$'):  # setting
            res = g_ATVSettings.getSetting(UDID, attrib[1:])
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

                if el.tag=='__COPY__':
                    for child in list(el):
                        elem.append(child)
                else:
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
        #PlexMgr = CPlexMgr.from_state(self.options['PlexConnectUDID'])
        PlexMgr = self.options['PlexMgr'][self.options['PlexConnectUDID']]
        tag, leftover = self.getParam(src, param)
        key, leftover, dfltd = self.getKey(src, srcXML, leftover)

        if key.startswith('/'):  # internal full path.
            path = key
        elif key == '':  # internal path
            path = self.path[srcXML]
        else:  # internal path, add-on
            path = self.path[srcXML] + '/' + key

        if key.startswith('myplexsections'):
            # parse from memory
            XMLroot = etree.fromstring(PlexMgr.getXML(False))

            # XML root to ElementTree
            PMS = etree.ElementTree(XMLroot)
        elif key.startswith('localsections'):
            # parse from memory
            XMLroot = etree.fromstring(PlexMgr.getXML(True))

            # XML root to ElementTree
            PMS = etree.ElementTree(XMLroot)
        else:
            PMS = XML_ReadFromURL(g_param['Addr_PMS'], path, PlexMgr.getTokenFromAddress(g_param['Addr_PMS']))

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

    def ATTRIB_BIGIMAGEURL(self, src, srcXML, param):
        key, leftover, dfltd = self.getKey(src, srcXML, param)
        return self.imageUrl(self.path[srcXML], key, 768, 768)

    def ATTRIB_IMAGEURL(self, src, srcXML, param):
        key, leftover, dfltd = self.getKey(src, srcXML, param)
        return self.imageUrl(self.path[srcXML], key, 384, 384)

    def imageUrl(self, path, key, width, height):
        #token = CPlexMgr.from_state(self.options['PlexConnectUDID']).getTokenFromAddress(g_param['Addr_PMS'])
        token =  PlexMgr = self.options['PlexMgr'][self.options['PlexConnectUDID']].getTokenFromAddress(g_param['Addr_PMS'])

        if key.startswith('/'):  # internal full path.
            if token=="":
                res = 'http://127.0.0.1:32400' + key
            else:
                res = 'http://' + g_param['Addr_PMS'] + key
        elif key.startswith('http://'):  # external address
            res = key
            hijack = g_param['HostToIntercept']
            if hijack in res:
                dprint(__name__, 1, "twisting...")
                hijack_twisted = hijack[::-1]
                res = res.replace(hijack, hijack_twisted)
                dprint(__name__, 1, res)
        else:
            if token=="":
                res = 'http://127.0.0.1:32400' + path + '/' + key
            else:
                res = 'http://' + g_param['Addr_PMS'] + path + '/' + key

        # This is bogus (note the extra path component) but ATV is stupid when it comes to caching images, it doesn't use querystrings.
        # Fortunately PMS is lenient...
        #
        if token=="":
            return 'http://' + g_param['Addr_PMS'] + '/photo/:/transcode/%s/?width=%d&height=%d&url=' % (quote_plus(res), width, height) + quote_plus(res)
        else:
            return res + "?X-Plex-Token=" + token


    def ATTRIB_URL(self, src, srcXML, param):
        key, leftover, dfltd = self.getKey(src, srcXML, param)
        if key.startswith('/'):  # internal full path.
            res = 'http://' + g_param['HostOfPlexConnect'] + key
        elif key.startswith('http://'):  # external address
            res = key
            hijack = g_param['HostToIntercept']
            if hijack in res:
                dprint(__name__, 1, "twisting...")
                hijack_twisted = hijack[::-1]
                res = res.replace(hijack, hijack_twisted)
                dprint(__name__, 1, res)
        elif key == '':  # internal path
            res = 'http://' + g_param['HostOfPlexConnect'] + self.path[srcXML]
        else:  # internal path, add-on
            res = 'http://' + g_param['HostOfPlexConnect'] + self.path[srcXML] + '/' + key
        return res

    def ATTRIB_MEDIAURL(self, src, srcXML, param):
        #PlexMgr = CPlexMgr.from_state(self.options['PlexConnectUDID'])
        PlexMgr = self.options['PlexMgr'][self.options['PlexConnectUDID']]
        token = PlexMgr.getTokenFromAddress(g_param['Addr_PMS'])
        Video, leftover = self.getElement(src, srcXML, param)

        if Video!=None:
            Media = Video.find('Media')

        # check "Media" element and get key
        if Media!=None:
            UDID = self.options['PlexConnectUDID']

            #grab the current settings.
            transcodequality = g_ATVSettings.getSetting(UDID, 'transcodequality')
            transcoderaction = g_ATVSettings.getSetting(UDID, 'transcoderaction')

            #if it's myplex, we should force transcode, disable directplay and set a reasonable speed.
            #todo: speed should be configurable.
            srv = PlexMgr.getServerByIP(g_param['Addr_PMS'])
            if token!="" and PlexMgr.isServerLocal(srv)==False:
                dprint(__name__, 0, "Changing Remote Transcode")
                g_ATVSettings.setSetting(UDID, 'transcodequality', '480p 2.0Mbps')
                g_ATVSettings.setSetting(UDID, 'transcoderaction', 'Transcode')


            if g_ATVSettings.getSetting(UDID, 'transcoderaction')=='DirectPlay' \
               or \
               g_ATVSettings.getSetting(UDID, 'transcoderaction')=='Auto' and \
               Media.get('protocol','-') in ("hls") \
               or \
               g_ATVSettings.getSetting(UDID, 'transcoderaction')=='Auto' and \
               Media.get('container','-') in ("mov", "mp4") and \
               Media.get('videoCodec','-') in ("mpeg4", "h264", "drmi") and \
               Media.get('audioCodec','-') in ("aac", "ac3", "drms"):
                # direct play for...
                #    force direct play
                # or HTTP live stream
                # or native aTV media
                res, leftover, dfltd = self.getKey(Media, srcXML, 'Part/key')

                if Media.get('indirect',None):  # indirect... todo: select suitable resolution, today we just take first Media
                    key, leftover, dfltd = self.getKey(Media, srcXML, 'Part/key')
                    PMS = XML_ReadFromURL(g_param['Addr_PMS'], key, PlexMgr.getTokenFromAddress(g_param['Addr_PMS']))  # todo... check key for trailing '/' or even 'http'
                    res, leftover, dfltd = self.getKey(PMS.getroot(), srcXML, 'Video/Media/Part/key')

            else:
                # request transcoding
                res = Video.get('key','')
                res = PlexAPI_getTranscodePath(self.options, res)

            #restore the settings
            if token!="":
                g_ATVSettings.setSetting(UDID, 'transcodequality', transcodequality)
                g_ATVSettings.setSetting(UDID, 'transcoderaction', transcoderaction)

        else:
            dprint(__name__, 0, "MEDIAPATH - element not found: {0}", param)
            res = 'FILE_NOT_FOUND'  # not found?

        if res.startswith('/'):  # internal full path.
            res = 'http://' + g_param['Addr_PMS'] + res
        elif res.startswith('http://'):  # external address
            hijack = g_param['HostToIntercept']
            if hijack in res:
                dprint(__name__, 1, "twisting...")
                hijack_twisted = hijack[::-1]
                res = res.replace(hijack, hijack_twisted)
                dprint(__name__, 1, res)
        else:  # internal path, add-on
            res = 'http://' + g_param['Addr_PMS'] + self.path[srcXML] + res
        return res

    def ATTRIB_ADDR_PMS(self, src, srcXML, param):
        return g_param['Addr_PMS']

    def ATTRIB_episodestring(self, src, srcXML, param):
        parentIndex, leftover, dfltd = self.getKey(src, srcXML, param)  # getKey "defaults" if nothing found.
        index, leftover, dfltd = self.getKey(src, srcXML, leftover)
        title, leftover, dfltd = self.getKey(src, srcXML, leftover)
        out = self._("{0:0d}x{1:02d} {2}").format(int(parentIndex), int(index), title)
        return out

    def ATTRIB_sendToATV(self, src, srcXML, param):
        ratingKey, leftover, dfltd = self.getKey(src, srcXML, param)  # getKey "defaults" if nothing found.
        duration, leftover, dfltd = self.getKey(src, srcXML, leftover)
        UDID = self.options['PlexConnectUDID']
        out = "atv.sessionStorage['ratingKey']='" + ratingKey + "';atv.sessionStorage['duration']='" + duration + "';" + \
              "atv.sessionStorage['showplayerclock']='" + g_ATVSettings.getSetting(UDID, 'showplayerclock') + "';" + \
              "atv.sessionStorage['showendtime']='" + g_ATVSettings.getSetting(UDID, 'showendtime') + "';" + \
              "atv.sessionStorage['overscanadjust']='" + g_ATVSettings.getSetting(UDID, 'overscanadjust') + "';" + \
              "atv.sessionStorage['clockposition']='" + g_ATVSettings.getSetting(UDID, 'clockposition') + "';" + \
              "atv.sessionStorage['timeformat']='" + g_ATVSettings.getSetting(UDID, 'timeformat') + "';"
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
        #return str(len(CPlexMgr.from_state(self.options['PlexConnectUDID']).servers))
        return str(len(self.options['PlexMgr'][self.options['PlexConnectUDID']].servers))

    def ATTRIB_PMSNAME(self, src, srcXML, param):

        UDID = self.options['PlexConnectUDID']
        #PlexMgr = CPlexMgr.from_state(UDID)
        PlexMgr = self.options['PlexMgr'][self.options['PlexConnectUDID']]
        PMS_uuid = g_ATVSettings.getSetting(UDID, 'pms_uuid')

        if len(PlexMgr.servers)==0:
            return "[no Server in Proximity]"
        else:
            PMS_uuid = g_ATVSettings.getSetting(self.options['PlexConnectUDID'], 'pms_uuid')
            pSrv = PlexMgr.getServerByUUID(PMS_uuid)
            if pSrv!=None:
                return pSrv.name.decode('utf-8', 'replace')  # return as utf-8
            else:
                return '[PMS_uuid not found]'



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
    options['PlexConnectUDID'] = '007'
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

    del cfg
