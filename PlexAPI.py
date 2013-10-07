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

from urllib import urlencode

from Debug import *  # dprint(), prettyXML()



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
                        update['serverName'] = each.split(':')[1].strip()
                    elif "Port:" in each:
                        update['port'] = each.split(':')[1].strip()
                    elif "Updated-At:" in each:
                        update['updated'] = each.split(':')[1].strip()
                    elif "Version:" in each:
                        update['version'] = each.split(':')[1].strip()
            
            PMS_list[update['uuid']] = update
    
    if PMS_list=={}:
        dprint(__name__, 0, "No servers discovered")
    else:
        dprint(__name__, 0, "servers discovered: {0}", len(PMS_list))
        for uuid in PMS_list:
            dprint(__name__, 1, "{0} {1}:{2}", PMS_list[uuid]['serverName'], PMS_list[uuid]['ip'], PMS_list[uuid]['port'])
    
    return PMS_list



"""
Plex Media Server communication

parameters:
    host
    path
result:
    returned XML or 'False' in case of error
"""
def getXMLFromPMS(host, path):
    xargs = getXArgsDeviceInfo()
    if path.find('?')>=0:
        path = path + '&' + urlencode(xargs)
    else:
        path = path + '?' + urlencode(xargs)
    
    URL = "http://" + host + path
    request = urllib2.Request(URL)
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



def getXArgsDeviceInfo(options=None):
    xargs = dict()
    xargs['X-Plex-Device'] = 'AppleTV'
    xargs['X-Plex-Model'] = '3,1' # Base it on AppleTV model.
    if not options is None:
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
    request = urllib2.Request(MyPlexURL)
    xargs = getXArgsDeviceInfo(options)
    for opt in xargs:
        request.add_header(opt, xargs[opt])
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
    request = urllib2.Request(MyPlexURL)
    request.add_header('X-Plex-Token', authtoken)
    request.get_method = lambda: 'POST'  # turn into 'POST' - done automatically with data!=None. But we don't have data.
    
    response = urllib2.urlopen(request).read()
    
    dprint(__name__, 1, "====== MyPlex sign out XML ======")
    dprint(__name__, 1, response)
    dprint(__name__, 1, "====== MyPlex sign out XML finished ======")
    dprint(__name__, 0, 'MyPlex Sign Out done')



"""
Transcoder support

parameters:
    path
    options - dict() of PlexConnect-options as received from aTV
    ATVSettings
result:
    final path to pull in PMS transcoder
"""
def getTranscodePath(path, options, ATVSettings):
    UDID = options['PlexConnectUDID']
    ###
    g_ATVSettings = ATVSettings
    ###
    
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
    
    xargs = getXArgsDeviceInfo(options)
    xargs['X-Plex-Client-Capabilities'] = "protocols=http-live-streaming,http-mp4-streaming,http-streaming-video,http-streaming-video-720p,http-mp4-video,http-mp4-video-720p;videoDecoders=h264{profile:high&resolution:1080&level:41};audioDecoders=mp3,aac{bitrate:160000}"
    
    return transcodePath + urlencode(args) + '&' + urlencode(xargs)



if __name__ == '__main__':
    # test PlexGDM
    print "*** PlexGDM"
    PMS_list = PlexGDM()
    print PMS_list
    
    # test "get PMS XML"
    
    # test MyPlex Sign in/Sign Out
    print "*** MyPlex"
    options = {'PlexConnectUDID':'007'}
    
    (name, token) = MyPlexSignIn('username', 'password', options)
    if name=='' and token=='':
        print "Authentication failed"
    else:
        print "logged in:", name, token
        
        MyPlexSignOut(token)
        print "logged out"
    
    # test transcoder