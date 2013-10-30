#!/usr/bin/env python

"""
Collection of "connector functions" to Plex Media Server/MyPlex


PlexGDM:
loosely based on hippojay's plexGDM:
https://github.com/hippojay/plugin.video.plexbmc


Plex Media Server communication:
source (somewhat): https://github.com/hippojay/plugin.video.plexbmc
later converted from httplib to urllib2


Transcoder support:
PlexAPI_getTranscodePath() based on getTranscodeURL from pyplex/plexAPI
https://github.com/megawubs/pyplex/blob/master/plexAPI/info.py


MyPlex - Basic Authentication:
http://www.voidspace.org.uk/python/articles/urllib2.shtml
http://www.voidspace.org.uk/python/articles/authentication.shtml
http://stackoverflow.com/questions/2407126/python-urllib2-basic-auth-problem
http://stackoverflow.com/questions/111945/is-there-any-way-to-do-http-put-in-python
(and others...)
"""



import sys
import struct
import urllib2, socket

try:
    import xml.etree.cElementTree as etree
except ImportError:
    import xml.etree.ElementTree as etree

from urllib import urlencode, quote_plus

from Debug import *  # dprint(), prettyXML()



"""
storage for PMS addresses and additional information - now per aTV! (replaces global PMS_list)
syntax: PMS[<ATV_UDID>][PMS_UUID][<data>]
    data: name, ip, ...type (local, myplex)
"""
g_PMS = {}


"""
Plex Media Server handling

parameters:
    ATV_udid
    uuid - PMS ID
    name, ip, port, type, token
"""
def declarePMS(ATV_udid, uuid, name, ip, port, type, token):
    # store PMS information in g_PMS database
    global g_PMS
    if not ATV_udid in g_PMS:
        g_PMS[ATV_udid] = {}
    
    address = ip + ':' + port
    g_PMS[ATV_udid][uuid] = { 'name': name,
                              'ip': ip , 'port': port, 'address': address,
                              'type': type,
                              'accessToken': token
                            }

def getPMSProperty(ATV_udid, uuid, tag):
    # get name of PMS by UUID
    if not ATV_udid in g_PMS:
        return ''  # no server known for this aTV
    if not uuid in g_PMS[ATV_udid]:
        return ''  # requested PMS not available
    
    return g_PMS[ATV_udid][uuid].get(tag, '')

def getPMSFromAddress(ATV_udid, address):
    # find PMS by IP, return UUID
    if not ATV_udid in g_PMS:
        return ''  # no server known for this aTV
    
    for uuid in g_PMS[ATV_udid]:
        if address==g_PMS[ATV_udid][uuid].get('address', None):
            return uuid
    return ''  # IP not found

def getPMSAddress(ATV_udid, uuid):
    # get address of PMS by UUID
    if not ATV_udid in g_PMS:
        return ''  # no server known for this aTV
    if not uuid in g_PMS[ATV_udid]:
        return ''  # requested PMS not available
    
    return g_PMS[ATV_udid][uuid]['ip'] + ':' + g_PMS[ATV_udid][uuid]['port']

def getPMSCount(ATV_udid):
    # get count of discovered PMS by UUID
    if not ATV_udid in g_PMS:
        return 0  # no server known for this aTV
    
    return len(g_PMS[ATV_udid])



"""
PlexGDM

parameters:
    none
result:
    PMS_list - dict() of PMSs found
"""
IP_PlexGDM = '<broadcast>'
Port_PlexGDM = 32414
Msg_PlexGDM = 'M-SEARCH * HTTP/1.0'

def PlexGDM():
    dprint(__name__, 0, "***")
    dprint(__name__, 0, "looking up Plex Media Server")
    dprint(__name__, 0, "***")
    
    # setup socket for discovery -> multicast message
    GDM = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    GDM.settimeout(1.0)
    
    # Set the time-to-live for messages to 1 for local network
    GDM.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    returnData = []
    try:
        # Send data to the multicast group
        dprint(__name__, 1, "Sending discovery message: {0}", Msg_PlexGDM)
        GDM.sendto(Msg_PlexGDM, (IP_PlexGDM, Port_PlexGDM))

        # Look for responses from all recipients
        while True:
            try:
                data, server = GDM.recvfrom(1024)
                dprint(__name__, 1, "Received data from {0}", server)
                dprint(__name__, 1, "Data received:\n {0}", data)
                returnData.append( { 'from' : server,
                                     'data' : data } )
            except socket.timeout:
                break
    finally:
        GDM.close()

    discovery_complete = True

    PMS_list = {}
    if returnData:
        for response in returnData:
            update = { 'ip' : response.get('from')[0] }
            
            # Check if we had a positive HTTP response                        
            if "200 OK" in response.get('data'):
                for each in response.get('data').split('\n'): 
                    # decode response data
                    update['discovery'] = "auto"
                    #update['owned']='1'
                    #update['master']= 1
                    #update['role']='master'
                    
                    if "Content-Type:" in each:
                        update['content-type'] = each.split(':')[1].strip()
                    elif "Resource-Identifier:" in each:
                        update['uuid'] = each.split(':')[1].strip()
                    elif "Name:" in each:
                        update['serverName'] = each.split(':')[1].strip().decode('utf-8', 'replace')  # store in utf-8
                    elif "Port:" in each:
                        update['port'] = each.split(':')[1].strip()
                    elif "Updated-At:" in each:
                        update['updated'] = each.split(':')[1].strip()
                    elif "Version:" in each:
                        update['version'] = each.split(':')[1].strip()
            
            PMS_list[update['uuid']] = update
    
    if PMS_list=={}:
        dprint(__name__, 0, "GDM: No servers discovered")
    else:
        dprint(__name__, 0, "GDM: Servers discovered: {0}", len(PMS_list))
        for uuid in PMS_list:
            dprint(__name__, 1, "{0} {1}:{2}", PMS_list[uuid]['serverName'], PMS_list[uuid]['ip'], PMS_list[uuid]['port'])
    
    return PMS_list



"""
discoverPMS

parameters:
    ATV_udid
    CSettings - for manual PMS configuration. this one looks strange.
    authtoken
result:
    g_PMS database for ATV_udid
"""
def discoverPMS(ATV_udid, CSettings, authtoken=''):
    global g_PMS
    g_PMS = {}
    
    #debug
    #declarePMS(ATV_udid, '2ndServer', '2ndServer', '192.168.178.22', '32400', 'local', 'token')
    #declarePMS(ATV_udid, 'remoteServer', 'remoteServer', '127.0.0.1', '1234', 'remote', 'token')
    #debug
    
    # local PMS
    if CSettings.getSetting('enable_plexgdm')=='False':
        # defined in setting.cfg
        ip = CSettings.getSetting('ip_pms')
        port = CSettings.getSetting('port_pms')
        declarePMS(ATV_udid,  'PMS_from_Settings', 'PMS_from_Settings', ip, port, 'local', authtoken)
    else:
        # PlexGDM
        PMS_list = PlexGDM()
        for uuid in PMS_list:
            PMS = PMS_list[uuid]
            declarePMS(ATV_udid, PMS['uuid'], PMS['serverName'], PMS['ip'], PMS['port'], 'local', authtoken)
    
    # MyPlex servers
    if not authtoken=='':
        XML = getXMLFromPMS('https://my.plexapp.com', '/pms/servers', None, authtoken)
        
        if XML==False:
            pass  # no data from MyPlex
        else:
            for Dir in XML.getiterator('Server'):
                uuid = Dir.get('machineIdentifier')
                name = Dir.get('name')
                ip = Dir.get('address')
                port = Dir.get('port')
                token = Dir.get('accessToken', authtoken)
                
                if not uuid in g_PMS.get(ATV_udid, {}):
                    declarePMS(ATV_udid, uuid, name, ip, port, 'myplex', token)
    
    # debug print all servers
    dprint(__name__, 0, "Servers (local+MyPlex): {0}", len(g_PMS[ATV_udid]))
    for uuid in g_PMS[ATV_udid]:
        dprint(__name__, 1, str(g_PMS[ATV_udid][uuid]))



"""
Plex Media Server communication

parameters:
    host
    path
    options - dict() of PlexConnect-options as received from aTV, None for no std. X-Plex-Args
    authtoken - authentication answer from MyPlex Sign In
result:
    returned XML or 'False' in case of error
"""
def getXMLFromPMS(baseURL, path, options={}, authtoken=''):
    xargs = {}
    if not options==None:
        xargs = getXArgsDeviceInfo(options)
    if not authtoken=='':
        xargs['X-Plex-Token'] = authtoken
    
    dprint(__name__, 1, "URL: {0}{1}", baseURL, path)
    dprint(__name__, 1, "xargs: {0}", xargs)
    
    request = urllib2.Request(baseURL+path , None, xargs)
    try:
        response = urllib2.urlopen(request)
    except urllib2.URLError as e:
        dprint(__name__, 0, 'No Response from Plex Media Server')
        if hasattr(e, 'reason'):
            dprint(__name__, 0, "We failed to reach a server. Reason: {0}", e.reason)
        elif hasattr(e, 'code'):
            dprint(__name__, 0, "The server couldn't fulfill the request. Error code: {0}", e.code)
        return False
    
    # parse into etree
    XML = etree.parse(response)
    
    dprint(__name__, 1, "====== received PMS-XML ======")
    dprint(__name__, 1, prettyXML(XML))
    dprint(__name__, 1, "====== PMS-XML finished ======")
    
    #XMLTree = etree.ElementTree(etree.fromstring(response))
    
    return XML



def getXArgsDeviceInfo(options={}):
    xargs = dict()
    xargs['X-Plex-Device'] = 'AppleTV'
    xargs['X-Plex-Model'] = '3,1' # Base it on AppleTV model.
    #if not options is None:
    if 'PlexConnectUDID' in options:
            xargs['X-Plex-Client-Identifier'] = options['PlexConnectUDID']  # UDID for MyPlex device identification
    if 'PlexConnectATVName' in options:
            xargs['X-Plex-Device-Name'] = options['PlexConnectATVName'] # "friendly" name: aTV-Settings->General->Name.
    xargs['X-Plex-Platform'] = 'iOS'
    xargs['X-Plex-Client-Platform'] = 'iOS'
    xargs['X-Plex-Platform-Version'] = '5.3' # Base it on AppleTV OS version.
    xargs['X-Plex-Product'] = 'PlexConnect'
    xargs['X-Plex-Version'] = '0.2'
    
    return xargs



"""
provide combined XML representation of local servers' XMLs, eg. /library/section

parameters:
    ATV_udid
    path
    options
    authtoken
result:
    XML
"""
def getXMLFromMultiplePMS(ATV_udid, path, options={}, authtoken=''):
    root = etree.Element("MediaConverter")
    root.set('friendlyName', 'localServers')
    
    for uuid in g_PMS.get(ATV_udid, {}):
        PMS = g_PMS[ATV_udid][uuid]
        if PMS['type']=='local':
            Server = etree.SubElement(root, 'Server')  # create "Server" node
            Server.set('name',    getPMSProperty(ATV_udid, uuid, 'name'))
            Server.set('address', getPMSProperty(ATV_udid, uuid, 'ip'))
            Server.set('port',    getPMSProperty(ATV_udid, uuid, 'port'))
            baseURL = 'http://' + getPMSAddress(ATV_udid, uuid)
            PMSaddr = 'PMS(' + getPMSAddress(ATV_udid, uuid) + ')'
            Server.set('searchKey', PMSaddr + getURL('', '', '/SearchForm.xml'))
            
            XML = getXMLFromPMS(baseURL, path, options, authtoken)
            if XML==False:
                Server.set('size',    '0')
            else:
                Server.set('size',    XML.getroot().get('size', '0'))
                
                for Dir in XML.getiterator('Directory'):  # copy "Directory" content, add PMS to links
                    Dir.set('key',    PMSaddr + getURL('', path, Dir.get('key')))
                    if 'thumb' in Dir.attrib:
                        Dir.set('thumb',  PMSaddr + getURL('', path, Dir.get('thumb')))
                    if 'art' in Dir.attrib:
                        Dir.set('art',    PMSaddr + getURL('', path, Dir.get('art')))
                    Server.append(Dir)
    
    root.set('size', str(len(root.findall('Server'))))
    
    XML = etree.ElementTree(root)
    
    dprint(__name__, 1, "====== Local Server/Sections XML ======")
    dprint(__name__, 1, prettyXML(XML))
    dprint(__name__, 1, "====== Local Server/Sections XML finished ======")
    
    return XML  # XML representation - created "just in time". Do we need to cache it?



def getURL(PMSaddress, path, key):
    if key.startswith('http://'):  # external server
        URL = key
    elif key.startswith('/'):  # internal full path.
        URL = PMSaddress + key
    elif key == '':  # internal path
        URL = PMSaddress + path
    else:  # internal path, add-on
        URL = PMSaddress + path + '/' + key
    
    return URL



"""
MyPlex Sign In, Sign Out

parameters:
    username - Plex forum name, MyPlex login, or email address
    password
    options - dict() of PlexConnect-options as received from aTV - necessary: PlexConnectUDID
result:
    username
    authtoken - token for subsequent communication with MyPlex
"""
def MyPlexSignIn(username, password, options):
    # MyPlex web address
    MyPlexHost = 'my.plexapp.com'
    MyPlexSignInPath = '/users/sign_in.xml'
    MyPlexURL = 'https://' + MyPlexHost + MyPlexSignInPath
    
    # create POST request
    xargs = getXArgsDeviceInfo(options)
    request = urllib2.Request(MyPlexURL, None, xargs)
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
        response = urlopener.open(request).read()
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
    
    el_username = XMLTree.find('username')
    el_authtoken = XMLTree.find('authentication-token')    
    if el_username is None or \
       el_authtoken is None:
        username = ''
        authtoken = ''
        dprint(__name__, 0, 'MyPlex Sign In failed')
    else:
        username = el_username.text
        authtoken = el_authtoken.text
        dprint(__name__, 0, 'MyPlex Sign In successfull')
    
    return (username, authtoken)



def MyPlexSignOut(authtoken):
    # MyPlex web address
    MyPlexHost = 'my.plexapp.com'
    MyPlexSignOutPath = '/users/sign_out.xml'
    MyPlexURL = 'http://' + MyPlexHost + MyPlexSignOutPath
    
    # create POST request
    xargs = { 'X-Plex-Token': authtoken }
    request = urllib2.Request(MyPlexURL, None, xargs)
    request.get_method = lambda: 'POST'  # turn into 'POST' - done automatically with data!=None. But we don't have data.
    
    response = urllib2.urlopen(request).read()
    
    dprint(__name__, 1, "====== MyPlex sign out XML ======")
    dprint(__name__, 1, response)
    dprint(__name__, 1, "====== MyPlex sign out XML finished ======")
    dprint(__name__, 0, 'MyPlex Sign Out done')



"""
Transcode Video support

parameters:
    path
    AuthToken
    options - dict() of PlexConnect-options as received from aTV
    ATVSettings
result:
    final path to pull in PMS transcoder
"""
def getTranscodeVideoPath(path, AuthToken, options, ATVSettings):
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
    setAction = ATVSettings.getSetting(UDID, 'transcoderaction')
    setQuality = ATVSettings.getSetting(UDID, 'transcodequality')
    vRes = quality[setQuality][0]
    vQ = quality[setQuality][1]
    mVB = quality[setQuality][2]
    dprint(__name__, 1, "Setting transcode quality Res:{0} Q:{1} {2}Mbps", vRes, vQ, mVB)
    sS = ATVSettings.getSetting(UDID, 'subtitlesize')
    dprint(__name__, 1, "Subtitle size: {0}", sS)
    aB = ATVSettings.getSetting(UDID, 'audioboost')
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
    
    xargs = getXArgsDeviceInfo(options)
    xargs['X-Plex-Client-Capabilities'] = "protocols=http-live-streaming,http-mp4-streaming,http-streaming-video,http-streaming-video-720p,http-mp4-video,http-mp4-video-720p;videoDecoders=h264{profile:high&resolution:1080&level:41};audioDecoders=mp3,aac{bitrate:160000}"
    if not AuthToken=='':
        xargs['X-Plex-Token'] = AuthToken
    
    return transcodePath + urlencode(args) + '&' + urlencode(xargs)



"""
Direct Video Play support

parameters:
    path
    AuthToken
    Indirect - media indirect specified, grab child XML to gain real path
    options
result:
    final path to media file
"""
def getDirectVideoPath(key, AuthToken):
    if key.startswith('http://'):  # external address - keep
        path = key
    else:
        if AuthToken=='':
            path = key
        else:
            xargs = dict()
            xargs['X-Plex-Token'] = AuthToken
            if key.find('?')==-1:
                path = key + '?' + urlencode(xargs)
            else:
                path = key + '&' + urlencode(xargs)
    
    return path



"""
Transcode Image support

parameters:
    key
    AuthToken
    path - source path of current XML: path[srcXML]
    width
    height
result:
    final path to image file
"""
def getTranscodeImagePath(key, AuthToken, path, width, height):
    if key.startswith('/'):  # internal full path.
        path = 'http://127.0.0.1:32400' + key
    elif key.startswith('http://'):  # external address - can we get a transcoding request for external images?
        path = key
    else:  # internal path, add-on
        path = 'http://127.0.0.1:32400' + path + '/' + key
    
    # This is bogus (note the extra path component) but ATV is stupid when it comes to caching images, it doesn't use querystrings.
    # Fortunately PMS is lenient...
    path = '/photo/:/transcode/%s/?width=%s&height=%s&url=' % (quote_plus(path), width, height) + quote_plus(path)
    
    if not AuthToken=='':
        xargs = dict()
        xargs['X-Plex-Token'] = AuthToken
        path = path + '&' + urlencode(xargs)
    
    return path



"""
Direct Image support

parameters:
    path
    AuthToken
result:
    final path to image file
"""
def getDirectImagePath(path, AuthToken):
    if not AuthToken=='':
        xargs = dict()
        xargs['X-Plex-Token'] = AuthToken
        if path.find('?')==-1:
            path = path + '?' + urlencode(xargs)
        else:
            path = path + '&' + urlencode(xargs)
    
    return path



"""
Direct Audio support

parameters:
    path
    AuthToken
result:
    final path to audio file
"""
def getDirectAudioPath(path, AuthToken):
    if not AuthToken=='':
        xargs = dict()
        xargs['X-Plex-Token'] = AuthToken
        if path.find('?')==-1:
            path = path + '?' + urlencode(xargs)
        else:
            path = path + '&' + urlencode(xargs)
    
    return path



if __name__ == '__main__':
    testPlexGDM = 0
    testLocalPMS = 0
    testSectionXML = 1
    testMyPlexXML = 0
    testMyPlexSignIn = 0
    testMyPlexSignOut = 0
    
    username = 'abc'
    password = 'def'
    token = 'xyz'
    
    
    # test PlexGDM
    if testPlexGDM:
        dprint('', 0, "*** PlexGDM")
        PMS_list = PlexGDM()
        dprint('', 0, PMS_list)
    
    
    # test XML from local PMS
    if testLocalPMS:
        dprint('', 0, "*** XML from local PMS")
        XML = getXMLFromPMS('http://127.0.0.1:32400', '/library/sections')
    
    
    # test local Server/Sections
    if testSectionXML:
        dprint('', 0, "*** local Server/Sections")
        PMS_list = PlexGDM()
        XML = getSectionXML(PMS_list, {}, '')
    
    
    # test XML from MyPlex
    if testMyPlexXML:
        dprint('', 0, "*** XML from MyPlex")
        XML = getXMLFromPMS('https://my.plexapp.com', '/pms/servers', None, token)
        XML = getXMLFromPMS('https://my.plexapp.com', '/pms/system/library/sections', None, token)
    
    
    # test MyPlex Sign In
    if testMyPlexSignIn:
        dprint('', 0, "*** MyPlex Sign In")
        options = {'PlexConnectUDID':'007'}
        
        (user, token) = MyPlexSignIn(username, password, options)
        if user=='' and token=='':
            dprint('', 0, "Authentication failed")
        else:
            dprint('', 0, "logged in: {0}, {1}", user, token)
    
    
    # test MyPlex Sign out
    if testMyPlexSignOut:
        dprint('', 0, "*** MyPlex Sign Out")
        MyPlexSignOut(token)
        dprint('', 0, "logged out")
    
    # test transcoder
