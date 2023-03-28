#!/usr/bin/env python

"""
Collection of "connector functions" to Plex Media Server/MyPlex


PlexGDM:
loosely based on hippojay's plexGDM:
https://github.com/hippojay/script.plexbmc.helper... /resources/lib/plexgdm.py


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
import time
import urllib2, httplib, socket, StringIO, gzip
from threading import Thread
import Queue
import traceback

try:
    import xml.etree.cElementTree as etree
except ImportError:
    import xml.etree.ElementTree as etree

from urllib import urlencode, quote_plus

from Version import __VERSION__
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
    name, scheme, ip, port, type, owned, token
"""
def declarePMS(ATV_udid, uuid, name, scheme, ip, port):
    # store PMS information in g_PMS database
    global g_PMS
    if not ATV_udid in g_PMS:
        g_PMS[ATV_udid] = {}
    
    address = ip + ':' + port
    baseURL = scheme+'://'+ip+':'+port
    g_PMS[ATV_udid][uuid] = { 'name': name,
                              'scheme':scheme, 'ip': ip , 'port': port,
                              'address': address,
                              'baseURL': baseURL,
                              'local': '1',
                              'owned': '1',
                              'accesstoken': '',
                              'enableGzip': False
                            }

def updatePMSProperty(ATV_udid, uuid, tag, value):
    # set property element of PMS by UUID
    if not ATV_udid in g_PMS:
        return ''  # no server known for this aTV
    if not uuid in g_PMS[ATV_udid]:
        return ''  # requested PMS not available
    
    g_PMS[ATV_udid][uuid][tag] = value

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
        if address in g_PMS[ATV_udid][uuid].get('address', None):
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
IP_PlexGDM = '239.0.0.250'  # multicast to PMS
Port_PlexGDM = 32414
Msg_PlexGDM = 'M-SEARCH * HTTP/1.0'

def PlexGDM():
    dprint(__name__, 0, "***")
    dprint(__name__, 0, "PlexGDM - looking up Plex Media Server")
    dprint(__name__, 0, "***")
    
    # setup socket for discovery -> multicast message
    GDM = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    GDM.settimeout(1.0)
    
    # Set the time-to-live for messages to 1 for local network
    ttl = struct.pack('b', 1)
    GDM.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
    
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
    IP_self
optional:
    tokenDict - dictionary of tokens for MyPlex, PlexHome
result:
    g_PMS database for ATV_udid
"""
def discoverPMS(ATV_udid, CSettings, IP_self, tokenDict={}):
    global g_PMS
    g_PMS[ATV_udid] = {}
    
    # install plex.tv "virtual" PMS - for myPlex, PlexHome
    declarePMS(ATV_udid, 'plex.tv', 'plex.tv', 'https', 'plex.tv', '443')
    updatePMSProperty(ATV_udid, 'plex.tv', 'local', '-')
    updatePMSProperty(ATV_udid, 'plex.tv', 'owned', '-')
    updatePMSProperty(ATV_udid, 'plex.tv', 'accesstoken', tokenDict.get('MyPlex', ''))
    
    #debug
    #declarePMS(ATV_udid, '2ndServer', '2ndServer', 'http', '192.168.178.22', '32400', 'local', '1', 'token')
    #declarePMS(ATV_udid, 'remoteServer', 'remoteServer', 'http', '127.0.0.1', '1234', 'myplex', '1', 'token')
    #debug
    
    if 'PlexHome' in tokenDict:
        authtoken = tokenDict.get('PlexHome')
    else:
        authtoken = tokenDict.get('MyPlex', '')
    
    if authtoken=='':
      # not logged into myPlex
      # local PMS
      if CSettings.getSetting('enable_plexgdm')=='False':
        # defined in setting.cfg
        ip = CSettings.getSetting('ip_pms')
        # resolve hostname if needed
        try:
            ip2 = socket.gethostbyname(ip)
            if ip != ip2:
                dprint(__name__, 0, "PlexAPI - Hostname "+ip+" resolved to "+ip2)
                ip = ip2
        except:
            dprint(__name__, 0, "PlexAPI - ip_dns "+ip+" could not be resolved")
            
        port = CSettings.getSetting('port_pms')
        XML = getXMLFromPMS('http://'+ip+':'+port, '/servers', None, '')
        
        if XML==False:
            pass  # no response from manual defined server (Settings.cfg)
        else:
            Server = XML.find('Server')
            uuid = Server.get('machineIdentifier')
            name = Server.get('name')
            
            declarePMS(ATV_udid, uuid, name, 'http', ip, port)  # dflt: token='', local, owned
            # todo - check IP to verify "local"?
      
      else:
        # PlexGDM
        PMS_list = PlexGDM()
        for uuid in PMS_list:
            PMS = PMS_list[uuid]
            declarePMS(ATV_udid, PMS['uuid'], PMS['serverName'], 'http', PMS['ip'], PMS['port'])  # dflt: token='', local, owned
    
    else:
        # MyPlex servers
        getPMSListFromMyPlex(ATV_udid, authtoken)
    
    # all servers - update enableGzip
    for uuid in g_PMS.get(ATV_udid, {}):
        # enable Gzip if not on same host, local&remote PMS depending on setting
        enableGzip = (not getPMSProperty(ATV_udid, uuid, 'ip')==IP_self) and ( \
                     (getPMSProperty(ATV_udid, uuid, 'local')=='1' and CSettings.getSetting('allow_gzip_pmslocal')=='True' ) or \
                     (getPMSProperty(ATV_udid, uuid, 'local')=='0' and CSettings.getSetting('allow_gzip_pmsremote')=='True') )
        updatePMSProperty(ATV_udid, uuid, 'enableGzip', enableGzip)
    
    # debug print all servers
    dprint(__name__, 0, "ATV ["+ATV_udid+"] Plex Media Servers found: {0}", len(g_PMS[ATV_udid])-1)
    for uuid in g_PMS[ATV_udid]:
        dprint(__name__, 1, str(g_PMS[ATV_udid][uuid]))



"""
getPMSListFromMyPlex

get Plex media Server List from plex.tv/pms/resources
poke every PMS at every given address (plex.tv tends to cache a LOT...)
-> by design this leads to numerous threads ending in URLErrors like <timed out> or <Connection refused>
"""
def getPMSListFromMyPlex(ATV_udid, authtoken):
    dprint(__name__, 0, "***")
    dprint(__name__, 0, "ATV ["+ATV_udid+"] poke for plex.tv - request Plex Media Server list")
    dprint(__name__, 0, "***")
    
    XML = getXMLFromPMS('https://plex.tv', '/api/resources?includeHttps=1', {}, authtoken)
    
    if XML==False:
        pass  # no data from MyPlex
    else:
        queue = Queue.Queue()
        threads = []
        PMSsPoked = 0
        
        for Dir in XML.getiterator('Device'):
            if Dir.get('product','') == "Plex Media Server" and Dir.get('provides','') == "server":
                uuid = Dir.get('clientIdentifier')
                name = Dir.get('name')
                token = Dir.get('accessToken', authtoken)
                owned = Dir.get('owned', '0')
                
                if Dir.find('Connection') == None:
                    continue  # no valid connection - skip
                
                PMSsPoked +=1
                
                # multiple connection possible - poke either one, fastest response wins
                for Con in Dir.getiterator('Connection'):
                    protocol = Con.get('protocol')
                    ip = Con.get('address')
                    port = Con.get('port')
                    uri = Con.get('uri')
                    local = Con.get('local')
                    
                    # change protocol and uri if in local
                    if local == "1":
                        protocol = "http"
                        uri = protocol + "://" + ip + ":" + port
                                        
                    # poke PMS, own thread for each poke
                    PMSInfo = { 'uuid': uuid, 'name': name, 'token': token, 'owned': owned, 'local': local, \
                            'protocol': protocol, 'ip': ip, 'port': port, 'uri': uri }
                    PMS = { 'baseURL': uri, 'path': '/', 'options': None, 'token': token, \
                            'data': PMSInfo }
                    dprint(__name__, 0, "poke {0} ({1}) at {2}", name, uuid, uri)
                    t = Thread(target=getXMLFromPMSToQueue, args=(PMS, queue))
                    t.start()
                    threads.append(t)
        
        # wait for requests being answered
        # - either all communication threads done
        # - or at least one response received from every PMS (early exit)
        ThreadsAlive = -1
        PMSsCnt = 0
        while ThreadsAlive != 0 and PMSsPoked != PMSsCnt:
            # check for "living" threads - basically a manual t.join()
            ThreadsAlive = 0
            for t in threads:
                if t.isAlive():
                    ThreadsAlive += 1
            
            # analyse PMS/http response - declare new PMS
            if not queue.empty():
                (PMSInfo, PMS) = queue.get()
                
                if PMS==False:
                    # communication error - skip this connection
                    continue
                
                uuid = PMSInfo['uuid']
                name = PMSInfo['name']
                
                if uuid != PMS.getroot().get('machineIdentifier') or \
                   name != PMS.getroot().get('friendlyName'):
                    # response from someone - but not the poked PMS - skip this connection
                    continue
                
                token = PMSInfo['token']
                owned = PMSInfo['owned']
                local = PMSInfo['local']
                protocol = PMSInfo['protocol']
                ip = PMSInfo['ip']
                port = PMSInfo['port']
                uri = PMSInfo['uri']
                    
                if not uuid in g_PMS[ATV_udid]:  # PMS uuid not yet handled, so take it
                    PMSsCnt += 1
                    
                    dprint(__name__, 0, "response {0} ({1}) at {2}", name, uuid, uri)
                    
                    declarePMS(ATV_udid, uuid, name, protocol, ip, port)  # dflt: token='', local, owned - updated later
                    updatePMSProperty(ATV_udid, uuid, 'accesstoken', token)
                    updatePMSProperty(ATV_udid, uuid, 'owned', owned)
                    updatePMSProperty(ATV_udid, uuid, 'local', local)
                    updatePMSProperty(ATV_udid, uuid, 'baseURL', uri)  # set in declarePMS, overwrite for https encryption
                elif local=='1':    # Update udid if local instance is found
                    
                    dprint(__name__, 0, "update to {0} ({1}) at {2}", name, uuid, uri)
                    
                    declarePMS(ATV_udid, uuid, name, protocol, ip, port)  # dflt: token='', local, owned - updated later
                    updatePMSProperty(ATV_udid, uuid, 'accesstoken', token)
                    updatePMSProperty(ATV_udid, uuid, 'owned', owned)
                    updatePMSProperty(ATV_udid, uuid, 'local', local)
                    updatePMSProperty(ATV_udid, uuid, 'baseURL', uri)  # set in declarePMS, overwrite for https encryption
                    
                    

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
def getXMLFromPMS(baseURL, path, options={}, authtoken='', enableGzip=False):
    xargs = {}
    if not options==None:
        xargs = getXArgsDeviceInfo(options)
    if not authtoken=='':
        xargs['X-Plex-Token'] = authtoken
    
    dprint(__name__, 1, "URL: {0}{1}", baseURL, path)
    dprint(__name__, 1, "xargs: {0}", xargs)

    method = 'GET'
    if options is not None and 'PlexConnectMethod' in options:
        dprint(__name__, 1, 'Custom method ' + method)
        method = options['PlexConnectMethod']
    
    request = urllib2.Request(baseURL+path , None, xargs)
    request.add_header('User-agent', 'PlexConnect')

    request.get_method = lambda: method
    if enableGzip:
        request.add_header('Accept-encoding', 'gzip')
    
    try:
        response = urllib2.urlopen(request, timeout=20)
    except (urllib2.URLError, httplib.HTTPException) as e:
        dprint(__name__, 1, 'No Response from Plex Media Server')
        if hasattr(e, 'reason'):
            dprint(__name__, 1, "We failed to reach a server. Reason: {0}", e.reason)
        elif hasattr(e, 'code'):
            dprint(__name__, 1, "The server couldn't fulfill the request. Error code: {0}", e.code)
        dprint(__name__, 1, 'Traceback:\n{0}', traceback.format_exc())
        return False
    except IOError:
        dprint(__name__, 0, 'Error loading response XML from Plex Media Server:\n{0}', traceback.format_exc())
        return False
    
    if response.info().get('Content-Encoding') == 'gzip':
        buf = StringIO.StringIO(response.read())
        file = gzip.GzipFile(fileobj=buf)
        XML = etree.parse(file)
    else:
        # parse into etree
        XML = etree.parse(response)
    
    dprint(__name__, 1, "====== received PMS-XML ======")
    dprint(__name__, 1, XML.getroot())
    dprint(__name__, 1, "====== PMS-XML finished ======")
    
    #XMLTree = etree.ElementTree(etree.fromstring(response))
    
    return XML



def getXMLFromPMSToQueue(PMS, queue):
    XML = getXMLFromPMS(PMS['baseURL'],PMS['path'],PMS['options'],PMS['token'])
    queue.put( (PMS['data'], XML) )



def getXArgsDeviceInfo(options={}):
    xargs = dict()
    xargs['X-Plex-Device'] = 'AppleTV'
    xargs['X-Plex-Model'] = '2,3' # Base it on AppleTV model.
    #if not options is None:
    if 'PlexConnectUDID' in options:
            xargs['X-Plex-Client-Identifier'] = options['PlexConnectUDID']  # UDID for MyPlex device identification
    if 'PlexConnectATVName' in options:
            xargs['X-Plex-Device-Name'] = options['PlexConnectATVName'] # "friendly" name: aTV-Settings->General->Name.
    xargs['X-Plex-Platform'] = 'iOS'
    xargs['X-Plex-Client-Platform'] = 'iOS'
    xargs['X-Plex-Client-Profile-Extra'] = 'add-transcode-target(type=MusicProfile&context=streaming&protocol=hls&container=mpegts&audioCodec=aac)+add-transcode-target(type=videoProfile&context=streaming&protocol=hls&container=mpegts&videoCodec=h264&audioCodec=aac,mp3&replace=true)'
    if 'DolbyDigital' in options:
        if options['DolbyDigital']:
            xargs['X-Plex-Client-Profile-Extra'] = 'add-transcode-target(type=MusicProfile&context=streaming&protocol=hls&container=mpegts&audioCodec=aac)+add-transcode-target(type=videoProfile&context=streaming&protocol=hls&container=mpegts&videoCodec=h264&audioCodec=ac3&replace=true)+add-limitation(scope=videoAudioCodec&scopeName=ac3&type=upperBound&name=audio.channels&value=6&onlyTranscodes=true&replace=true)'
    if 'aTVFirmwareVersion' in options:
        xargs['X-Plex-Platform-Version'] = options['aTVFirmwareVersion']
    xargs['X-Plex-Product'] = 'PlexConnect'
    xargs['X-Plex-Version'] = __VERSION__
    
    return xargs



"""
provide combined XML representation of local servers' XMLs, eg. /library/section

parameters:
    ATV_udid
    path
    type - owned <> shared (previously: local, myplex)
    options
result:
    XML
"""
def getXMLFromMultiplePMS(ATV_udid, path, type, options={}):
    queue = Queue.Queue()
    threads = []
    
    root = etree.Element("MediaConverter")
    root.set('friendlyName', type+' Servers')
    
    for uuid in g_PMS.get(ATV_udid, {}):
        if (type=='all' and getPMSProperty(ATV_udid, uuid, 'name')!='plex.tv') or \
           (type=='owned' and getPMSProperty(ATV_udid, uuid, 'owned')=='1') or \
           (type=='shared' and getPMSProperty(ATV_udid, uuid, 'owned')=='0') or \
           (type=='local' and getPMSProperty(ATV_udid, uuid, 'local')=='1') or \
           (type=='remote' and getPMSProperty(ATV_udid, uuid, 'local')=='0'):
            Server = etree.SubElement(root, 'Server')  # create "Server" node
            Server.set('name',    getPMSProperty(ATV_udid, uuid, 'name'))
            Server.set('address', getPMSProperty(ATV_udid, uuid, 'ip'))
            Server.set('port',    getPMSProperty(ATV_udid, uuid, 'port'))
            Server.set('baseURL', getPMSProperty(ATV_udid, uuid, 'baseURL'))
            Server.set('local',   getPMSProperty(ATV_udid, uuid, 'local'))
            Server.set('owned',   getPMSProperty(ATV_udid, uuid, 'owned'))
            
            baseURL = getPMSProperty(ATV_udid, uuid, 'baseURL')
            token = getPMSProperty(ATV_udid, uuid, 'accesstoken')
            PMS_mark = 'PMS(' + getPMSProperty(ATV_udid, uuid, 'address') + ')'
            
            Server.set('searchKey', PMS_mark + getURL('', '', '/Search/Entry.xml'))
            
            # request XMLs, one thread for each
            PMS = { 'baseURL':baseURL, 'path':path, 'options':options, 'token':token, \
                    'data': {'uuid': uuid, 'Server': Server} }
            t = Thread(target=getXMLFromPMSToQueue, args=(PMS, queue))
            t.start()
            threads.append(t)
    
    # wait for requests being answered
    for t in threads:
        t.join()
    
    # add new data to root XML, individual Server
    while not queue.empty():
            (data, XML) = queue.get()
            uuid = data['uuid']
            Server = data['Server']

            baseURL = getPMSProperty(ATV_udid, uuid, 'baseURL')
            token = getPMSProperty(ATV_udid, uuid, 'accesstoken')
            PMS_mark = 'PMS(' + getPMSProperty(ATV_udid, uuid, 'address') + ')'
            
            if XML==False:
                Server.set('size',    '0')
            else:
                Server.set('size',    XML.getroot().get('size', '0'))
                
                for Dir in XML.getiterator('Directory'):  # copy "Directory" content, add PMS to links

                    if Dir.get('key') is not None and (Dir.get('agent') is not None or Dir.get('share') is not None):
                        key = Dir.get('key')  # absolute path
                        Dir.set('key',    PMS_mark + getURL('', path, key))
                        Dir.set('refreshKey', getURL(baseURL, path, key) + '/refresh')
                        if 'thumb' in Dir.attrib:
                            Dir.set('thumb',  PMS_mark + getURL('', path, Dir.get('thumb')))
                        if 'art' in Dir.attrib:
                            Dir.set('art',    PMS_mark + getURL('', path, Dir.get('art')))
                        # print Dir.get('type')
                        Server.append(Dir)
                    elif Dir.get('title') == 'Live TV & DVR':
                        mp = None
                        for MediaProvider in XML.getiterator('MediaProvider'):
                            if MediaProvider.get('protocols') == 'livetv':
                                mp = MediaProvider
                                break
                        if mp is not None:
                            Dir.set('key', PMS_mark + getURL('', '', mp.get('identifier')))
                            Dir.set('refreshKey', getURL(baseURL, '/livetv/dvrs', mp.get('parentID')) + '/reloadGuide')
                            Dir.set('scanner', 'PlexConnect LiveTV Scanner Placeholder')
                            Dir.set('type', 'livetv')
                            Dir.set('thumbType', 'video')
                            Server.append(Dir)
                            
                for Playlist in XML.getiterator('Playlist'):  # copy "Playlist" content, add PMS to links
                    key = Playlist.get('key')  # absolute path
                    Playlist.set('key',    PMS_mark + getURL('', path, key))
                    if 'composite' in Playlist.attrib:
                        Playlist.set('composite', PMS_mark + getURL('', path, Playlist.get('composite')))
                    Server.append(Playlist)
                
                for Video in XML.getiterator('Video'):  # copy "Video" content, add PMS to links
                    key = Video.get('key')  # absolute path
                    Video.set('key',    PMS_mark + getURL('', path, key))
                    if 'thumb' in Video.attrib:
                        Video.set('thumb', PMS_mark + getURL('', path, Video.get('thumb')))
                    if 'parentKey' in Video.attrib:
                        Video.set('parentKey', PMS_mark + getURL('', path, Video.get('parentKey')))
                    if 'parentThumb' in Video.attrib:
                        Video.set('parentThumb', PMS_mark + getURL('', path, Video.get('parentThumb')))
                    if 'grandparentKey' in Video.attrib:
                        Video.set('grandparentKey', PMS_mark + getURL('', path, Video.get('grandparentKey')))
                    if 'grandparentThumb' in Video.attrib:
                        Video.set('grandparentThumb', PMS_mark + getURL('', path, Video.get('grandparentThumb')))
                    Server.append(Video)
    
    root.set('size', str(len(root.findall('Server'))))
    
    XML = etree.ElementTree(root)
    
    dprint(__name__, 1, "====== Local Server/Sections XML ======")
    dprint(__name__, 1, XML.getroot())
    dprint(__name__, 1, "====== Local Server/Sections XML finished ======")
    
    return XML  # XML representation - created "just in time". Do we need to cache it?



def getURL(baseURL, path, key):
    if key.startswith('http://') or key.startswith('https://'):  # external server
        URL = key
    elif key.startswith('/'):  # internal full path.
        URL = baseURL + key
    elif key == '':  # internal path
        URL = baseURL + path
    else:  # internal path, add-on
        URL = baseURL + path + '/' + key
    
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
    MyPlexHost = 'plex.tv'
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
    passmanager.add_password(MyPlexHost, MyPlexURL, username, password)  # realm = 'plex.tv'
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
    MyPlexHost = 'plex.tv'
    MyPlexSignOutPath = '/api/v2/users/signout'
    MyPlexURL = 'http://' + MyPlexHost + MyPlexSignOutPath
    
    # create POST request
    xargs = { 'X-Plex-Token': authtoken }
    request = urllib2.Request(MyPlexURL, None, xargs)
    request.get_method = lambda: 'DELETE'  # turn into 'DELETE' - done automatically with data!=None. But we don't have data.
    
    response = urllib2.urlopen(request).read()
    
    dprint(__name__, 1, "====== MyPlex sign out XML ======")
    dprint(__name__, 1, response)
    dprint(__name__, 1, "====== MyPlex sign out XML finished ======")
    dprint(__name__, 0, 'MyPlex Sign Out done')



def MyPlexSwitchHomeUser(id, pin, options, authtoken):
    MyPlexHost = 'https://plex.tv'
    MyPlexURL = MyPlexHost + '/api/home/users/' + id + '/switch'
    
    if pin:
        MyPlexURL += '?pin=' + pin
    
    xargs = {}
    if options:
        xargs = getXArgsDeviceInfo(options)
    xargs['X-Plex-Token'] = authtoken
    
    request = urllib2.Request(MyPlexURL, None, xargs)
    request.get_method = lambda: 'POST'  # turn into 'POST' - done automatically with data!=None. But we don't have data.
    
    response = urllib2.urlopen(request).read()
    
    dprint(__name__, 1, "====== MyPlexHomeUser XML ======")
    dprint(__name__, 1, response)
    dprint(__name__, 1, "====== MyPlexHomeUser XML finished ======")
    
    # analyse response
    XMLTree = etree.ElementTree(etree.fromstring(response))
    
    el_user = XMLTree.getroot()  # root=<user>. double check?
    username = el_user.attrib.get('title', '')
    authtoken = el_user.attrib.get('authenticationToken', '')
    
    if username and authtoken:
        dprint(__name__, 0, 'MyPlex switch HomeUser change successfull')
    else:
        dprint(__name__, 0, 'MyPlex switch HomeUser change failed')
    
    return (username, authtoken)



"""
Transcode Video support

parameters:
    path
    AuthToken
    options - dict() of PlexConnect-options as received from aTV
    action - transcoder action: Auto, Directplay, Transcode
    quality - (resolution, quality, bitrate)
    subtitle - {'selected', 'dontBurnIn', 'size'}
    audio - {'boost'}
result:
    final path to pull in PMS transcoder
"""
def getTranscodeVideoPath(path, AuthToken, options, action, quality, subtitle, audio, partIndex):
    UDID = options['PlexConnectUDID']
    
    transcodePath = '/video/:/transcode/universal/start.m3u8?'
    
    vRes = quality[0]
    vQ = quality[1]
    mVB = quality[2]
    dprint(__name__, 1, "Setting transcode quality Res:{0} Q:{1} {2}Mbps", vRes, vQ, mVB)
    dprint(__name__, 1, "Subtitle: selected {0}, dontBurnIn {1}, size {2}", subtitle['selected'], subtitle['dontBurnIn'], subtitle['size'])
    dprint(__name__, 1, "Audio: boost {0}", audio['boost'])
    
    args = dict()
    args['session'] = UDID
    args['protocol'] = 'hls'
    args['videoResolution'] = vRes
    args['maxVideoBitrate'] = mVB
    args['videoQuality'] = vQ
    args['mediaBufferSize'] = '80000'
    args['directStream'] = '0' if action=='Transcode' else '1'
    # 'directPlay' - handled by the client in MEDIARUL()
    args['subtitleSize'] = subtitle['size']
    args['skipSubtitles'] = subtitle['dontBurnIn']  #'1'  # shut off PMS subtitles. Todo: skip only for aTV native/SRT (or other supported)
    args['audioBoost'] = audio['boost']
    args['fastSeek'] = '1'
    args['path'] = path
    args['partIndex'] = partIndex
    
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
    if key.startswith('http://') or key.startswith('https://'):  # external address - keep
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
    if key.startswith('http://') or key.startswith('https://'):  # external address - can we get a transcoding request for external images?
        path = key
    elif key.startswith('/'):  # internal full path.
        path = 'http://127.0.0.1:32400' + key
    else:  # internal path, add-on
        path = 'http://127.0.0.1:32400' + path + '/' + key
    path = path.encode('utf8')
    
    args = dict()
    args['width'] = width
    args['height'] = height
    args['url'] = path
    
    if not AuthToken=='':
        args['X-Plex-Token'] = AuthToken
    
    # ATV's cache ignores query strings, it does not ignore fragments though, so append the query as fragment as well.
    return '/photo/:/transcode' + '?' + urlencode(args) + '#' + urlencode(args)



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
Transcode Audio support

parameters:
    path
    AuthToken
    options - dict() of PlexConnect-options as received from aTV
    maxAudioBitrate - [kbps]
result:
    final path to pull in PMS transcoder
"""
def getTranscodeAudioPath(path, AuthToken, options, maxAudioBitrate):
    UDID = options['PlexConnectUDID']
    
    transcodePath = '/music/:/transcode/universal/start.mp3?'
    
    args = dict()
    args['path'] = path
    args['session'] = UDID
    args['protocol'] = 'hls'
    args['maxAudioBitrate'] = maxAudioBitrate
    
    xargs = getXArgsDeviceInfo(options)
    if not AuthToken=='':
        xargs['X-Plex-Token'] = AuthToken
    
    return transcodePath + urlencode(args) + '&' + urlencode(xargs)



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
        XML = getXMLFromPMS('https://plex.tv', '/pms/servers', None, token)
        XML = getXMLFromPMS('https://plex.tv', '/pms/system/library/sections', None, token)
    
    
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
