#!/usr/bin/env python

from Debug import * #dprint()
from urllib2 import urlopen

from httplib import HTTPSConnection
from httplib import HTTPConnection

try:
    import cpickle as pickle
except ImportError:
    import pickle
    
import pickle
import socket
from datetime import datetime
import xml.dom.minidom

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

import utils

MyPlexURL = 'my.plexapp.com'

#A simple class to contain a section.
class CSection():            
    def __init__(self, title, type, key):
        self.title = title
        self.type = type
        self.key = key
        dprint(__name__, 2, "Init class CSection")

#A not-so simple class to contain a server.        
class CServer():
    def __init__(self, uuid, name, address, port, token):
        #list to hold sections
        self.sections = []
        
        #server settings
        self.uuid = uuid
        self.name = name
        self.address = address
        self.port = port
        self.token = token
        
        #cache
        self.lastSection = None
        dprint(__name__, 2, "Init class CServer")
    
    def setToken(self, token):
        self.token = token

    def discoverSections(self, force=False):
        if self.lastSection!=None and (datetime.now() - self.lastSection).total_seconds()<3600 and force==False:
            dprint(__name__, 0, "Nothing doing. Cache time less than 1h threshold")
            return
        #we're here, so let's get the list of sections.
        self.sections = []
        #start by grabbing a reference to this server.
        dprint(__name__, 2, "Add: {0}, port: {1}", self.address, self.port)
        conn = HTTPConnection(self.address + ":" + self.port)
        path = '/library/sections'
        headers = {}
        
        if self.token!=None:
            headers = {'X-Plex-Token' : self.token}
                
        try:
            conn.request('GET', path, None, headers)
            responseXML = str(conn.getresponse().read())
        except:
            dprint(__name__, 0, 'No Response from myPlex Server')
            return False
                    
        #get the XML
        root = ET.fromstring(responseXML)
                    
        #and parse it
        XML = ET.ElementTree(root)
        
        for dir in XML.findall("Directory"):
            #and add the sections
            self.sections.append(CSection(dir.get('title'), dir.get('type'), dir.get('key')))
            dprint(__name__, 2, "{0} : Found section: {1}", self.name, dir.get('title'))

    def isMyPlex(self):
        return self.token != None

    def getSearchXML(self, query):
        #this function will return the search XML for this server.
        passthruURL = 'http://atv.plexconnect/passthru?URL=http://' + self.address + ':' + self.port
        conn = HTTPConnection(self.address + ":" + self.port)
        path = '/search?type=4&query=' + query
        headers = {}
                
        if self.token!=None:
            headers = {'X-Plex-Token' : self.token}
                        
        try:
            conn.request('GET', path, None, headers)
            responseXML = str(conn.getresponse().read())
        except:
            dprint(__name__, 0, 'No Response from myPlex Server')
            return False
                            
        #get the XML
        root = ET.fromstring(responseXML)
                            
        #and parse it
        XML = ET.ElementTree(root)
        for vid in XML.findall('Video'):
            vid.set('key', passthruURL + vid.get('key'))
            #Will need to fix art/thumb here...
            
        for part in XML.iter('Part'):
            part.set('key', passthruURL + part.get('key'))
            
        return ET.tostring(root)
            
    def sectionsToXML(self):
        #this function actually turns all the sections into a malformed chunk of XML. 
        #TODO: Learn how to actually parse XML.
        sectionXML = ""
        accessToken = "TKN_myplex_TKN"
        if self.token!=None:
            accessToken = self.token
        for section in self.sections:
            root = ET.Element("Directory", 
                              title=section.title,
                              machineIdentifier=self.uuid,
                              key='http://'+self.address+':'+self.port+'/library/sections/'+section.key,
                              accessToken=accessToken,
                              path='/library/sections/'+section.key,
                              serverName=self.name,
                              port=self.port,
                              address=self.address,
                              type=section.type)
            sectionXML += str(ET.tostring(root))
        return sectionXML
            
        
#An overall management class.
class CPlexMgr():
    def __init__(self, udid):
        dprint(__name__, 2, "Init class CPlexMgr")
        
        #Constructor
        #lists to hold local and myPlex servers
        self.servers = []
        self.sharedServers = []
        
        #per-atv setting reference
        self.atvUDID = udid
        
        #myPlex stuff
        self.myplex_user = None
        self.myplex_token = None
        
        #simple caching
        self.lastPMS = None
        self.lastmyPlex = None
        
        #keep it together
        self.currentServer = "Preferred"

    #a constructor that will attempt to create the manager with preserved state.    
    @classmethod
    def from_state(cls, udid):
        try:
            dprint(__name__, 2, "Attempting to restore state...")
            dprint(__name__, 2, "Opening File...")
            f = open(udid + '.p', 'rb')
            dprint(__name__, 2, "Attempting unpickle...")
            cls = pickle.load(f)
            f.close()
            dprint(__name__, 2, "State restored successfully!")
            return cls
        except:
            dprint(__name__, 2, "Unable to restore state")
            return cls(udid)
         
    #destructor that automatically saves the state.
    def __del__(self):
        f = open(self.atvUDID + '.p', 'wb')
        pickle.dump(self, f)
        f.close()
        dprint(__name__, 2, "Deinit class CPlexMgr")

    #debug function to get a list of servers.            
    def listServers(self):
        for server in self.servers:
            dprint(__name__, 0, "Local: {0}", server.name)
        for server in self.sharedServers:
            dprint(__name__, 0, "myPlex: {0}", server.name)
    
    #returns an XML dump of all the local or myPlex libraries. I'm using it in Directory.xml as an example.
    #In order to use this in Directory.xml, I had to make a quick modification to ADDXML in XMLConverter.py
    def getXML(self, local=True):
        #TODO: learn how to do proper XML construction in python
        responseXML = ""
        friendlyName = "Local"
        if local==True:
            for server in self.servers:
                responseXML += server.sectionsToXML()
               
        else:
            for server in self.sharedServers:
                responseXML += server.sectionsToXML()
            friendlyName = "myPlex"
                
        #figure out how many entries..
        size = responseXML.count('<Directory')
        
        root = ET.Element("MediaContainer", 
                          size=str(size),
                          friendlyName=friendlyName,
                          title1=friendlyName + ' Library')
        b = ET.SubElement(root,"replace")
        
        retVal = '<?xml version="1.0" encoding="UTF-8"?>' + str(ET.tostring(root))
        
        #TODO: Double Check Applicability. Might not be necessary to set to self.myplex_token
        if self.myplex_token==None:
            responseXML = responseXML.replace("TKN_myplex_TKN", "")
        else:
            responseXML = responseXML.replace("TKN_myplex_TKN", self.myplex_token)
        
        retVal = retVal.replace("<replace />", responseXML)
        
        return retVal
    
    #given an address or address:port combo, this returns a myplex token.
    def getTokenFromAddress(self, address):
        if address.find(':')==-1:
            for server in self.sharedServers:
                if server.address==address:
                    return server.token
        else:
            for server in self.sharedServers:
                if server.address==address.split(":")[0]:
                    return server.token
        return ""

    #login to myplex.
    def myPlexLogin(self, username, password):
        dprint(__name__, 0, "Attempt to log in to MyPlex!")
        
        opener = utils.BasicAuth()
        opener.setpasswd(username, password)
        # add our headers
        opener.addheader('X-Plex-Client-Identifier', self.atvUDID) 
        opener.addheader('X-Plex-Product', 'PlexConnect')
        opener.addheader('X-Plex-Version', '0.2')
        opener.addheader('X-Plex-Platform', 'iOS')
        opener.addheader('X-Plex-Device', 'AppleTV3,1')
        opener.addheader('X-Plex-Platform-Version', '5.3')
        
        # use the opener to fetch a URL
        try:
            responseXML = str(opener.open('https://' + MyPlexURL + '/users/sign_in.xml', {}).read())
            root = ET.fromstring(responseXML)
            self.myplex_token = root.findall('authentication-token')[0].text
            self.myplex_user = root.findall('username')[0].text
            dprint(__name__, 0, "Logged into myPlex as {0}", self.myplex_user)
            
            return True
        except:
            dprint(__name__, 0, "Unable to log into myPlex")
            #do logoff stuff
            self.myPlexLogout
            return False
    
    def myPlexLogout(self):
        self.myplex_token = None
        self.myplex_user = None
        sharedServers = []
        
    def myPlexLoggedIn(self):
        return self.myplex_token!=None

    #I basically recreated GDM into this - reused a lot of the code, so credit to the original author, but
    #moved the list from a global to a per-atv setting. 
    #If you don't "force" the discovery, it will only do it once an hour
    def discoverPMS(self, force=False, staticServer=None, staticPort=None):
        if self.lastPMS!=None and (datetime.now() - self.lastPMS).total_seconds()<3600 and force==False:
            dprint(__name__, 0, "Nothing doing. Cache time less than 1h threshold")
            return
        
        self.servers = []
        
       
        if staticServer!=None:
            PMS_uuid = 'PMS_from_Settings'
            port = "32400"
            if staticPort!=None:
                port = staticPort
            self.addLocalServer(PMS_uuid, PMS_uuid, staticServer, port, None)
            dprint(__name__, 0, "PlexGDM off - PMS from settings: {0}:{1}", self.getServerByUUID(PMS_uuid).address, self.getServerByUUID(PMS_uuid).port)
    
        else:
            #Based on GDM, adapted for CServer class.
            IP_PlexGDM = '<broadcast>'
            Port_PlexGDM = 32414
            Msg_PlexGDM = 'M-SEARCH * HTTP/1.0'

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
            
            #discovery_complete = True #This is not being used in PlexConnect
            
            if returnData:
                for response in returnData:
                    GDM_IP = response.get('from')[0]
    
                    # Check if we had a positive HTTP response                        
                    if "200 OK" in response.get('data'):
                        for each in response.get('data').split('\n'): 
                            if "Resource-Identifier:" in each:
                                GDM_UUID = each.split(':')[1].strip()
                            elif "Name:" in each:
                                GDM_NAME = each.split(':')[1].strip()
                            elif "Port:" in each:
                                GDM_PORT = each.split(':')[1].strip()
                        
                    self.addLocalServer(GDM_UUID, GDM_NAME, GDM_IP, GDM_PORT, None)
                
            if self.servers==[]:
                dprint(__name__, 0, "GDM: No servers discovered")
            else:
                dprint(__name__, 0, "GDM: {0} servers discovered", len(self.servers))

        #hold on to time for caching
        self.lastPMS = datetime.now()
        return len(self.servers)>0

    #get a list of all the local server uuid's - for the settings menu.
    def getLocalServerNames(self):
        opts = ()
        if len(self.servers)==0:
            opts = ('no_PMS_found', )
        else:    
            for server in self.servers:
                opts = opts + (server.uuid, )
        
        return opts

    #something like GDM for myPlex.        
    def discovermyPlex(self, force=False):
        if self.myPlexLoggedIn():
            if self.lastmyPlex!=None and (datetime.now() - self.lastmyPlex).total_seconds()<3600 and force==False:
                dprint(__name__, 0, "Nothing doing. Cache time less than 1h threshold")
                return
                
            self.sharedServers = []
            #start by grabbing a server list.
            conn = HTTPSConnection(MyPlexURL)
            path = '/pms/servers'
            headers = {'X-Plex-Token' : self.myplex_token}
        
            try:
                conn.request('GET', path, None, headers)
                responseXML = str(conn.getresponse().read())
            except:
                dprint(__name__, 0, 'No Response from myPlex Server')
                return False
            
            #get the XML
            root = ET.fromstring(responseXML)
            
            #and parse it
            XML = ET.ElementTree(root)
            
            for server in XML.findall("Server"):
                #grab uuid, serverName, ipaddress, port and authtoken.
                #first test. Let's see if the server is local.
                if server.get('address')==utils.getExternalIP():
                    #if we're here, it means that a myPlex server is actually local
                    if self.getServerByUUID(server.get('machineIdentifier'))!=None:
                        dprint(__name__, 0, "Not adding server: {0} - Already in Local List", server.get('name'))
                        dprint(__name__, 0, "Updating token..")
                        self.getServerByUUID(server.get('machineIdentifier')).setToken(server.get('token'))
                    else:
                        if server.get('localAddresses').find(',')==-1:
                            #Add the server.
                            self.addLocalServer(server.get('machineIdentifier'), server.get('name'), server.get('localAddresses'), server.get('port'), server.get('accessToken'))
                            dprint(__name__, 0, " myPlex - found local library: {0}:{1}", self.getServerByUUID(server.get('machineIdentifier')).address, self.getServer(server.get('machineIdentifier')).port)
                        else:
                            #Just grab the first local address
                            #TODO: Other clients will hit all local addresses looking for lowest latency and decide that way.
                            self.addLocalServer(server.get('machineIdentifier'), server.get('name'), server.get('localAddresses').split(',')[0], server.get('port'), server.get('accessToken'))
                            dprint(__name__, 0, " myPlex - found local library: {0}:{1}", self.getServerByUUID(server.get('machineIdentifier')).address, self.getServer(server.get('machineIdentifier')).port)
                else:
                    if self.getServerByUUID(server.get('machineIdentifier'))!=None:
                        dprint(__name__, 0, "Not adding server: {0} - Already in myPlex List", server.get('name'))
                    else:
                        #if we're here, it's a remote myPlex server.
                        self.addRemoteServer(server.get('machineIdentifier'), server.get('name'), server.get('address'), server.get('port'), server.get('accessToken'))
                        dprint(__name__, 0, " myPlex - found remote library: {0}:{1}", self.getServerByUUID(server.get('machineIdentifier')).address, self.getServerByUUID(server.get('machineIdentifier')).port)
        
            self.lastmyPlex = datetime.now()

    #add the server to the list and grab the sections immediately.        
    def addLocalServer(self, uuid, name, address, port, token):
        newServer = CServer(uuid, name, address, port, token)
        newServer.discoverSections()
        self.servers.append(newServer)
        
    def addRemoteServer(self, uuid, name, address, port, token):
        newServer = CServer(uuid, name, address, port, token)
        newServer.discoverSections()
        self.sharedServers.append(newServer)
    
    #return a handle to a server class, given a UUID, or returns None if the server doesn't exist.
    def getServerByUUID(self, uuid):
        for server in self.servers:
            if server.uuid==uuid:
                return server
        for server in self.sharedServers:
            if server.uuid==uuid:
                return server
        
        return None

    #return a handle to a server class, given an IP.
    def getServerByIP(self, ip):
        for server in self.servers:
            if server.address==ip:
                return server
        for server in self.sharedServers:
            if server.address==ip:
                return server
        return None

    def isServerLocal(self, server):
        for srv in self.servers:
            if srv==server:
                return True
                
        #you'll make it here if you never find a server.    
        return False

    #work in progress - nothing to see here yet.
    def searchAllServers(self, query):
        xml_combined = None
        for server in self.servers:
            root = ET.fromstring(server.getSearchXML(query))
            data = ET.ElementTree(root).getchildren()
            
            for cont in data.iter('MediaContainer'):
                if xml_combined is None:
                    xml_combined = data
                    #insertion_point = xml_combined.findall("./MediaContainer")[0]
                    insertion_point = data
                else:
                    insertion_point.append(cont)

        for server in self.sharedServers:
            data = ET.ElementTree(ET.fromstring(server.getSearchXML(query)))

            for cont in data.iter('MediaContainer'):
                if xml_combined is None:
                    xml_combined = data
                    #insertion_point = xml_combined.findall("./MediaContainer")[0]
                    insertion_point = data
                else:
                    insertion_point.append(cont)

        dprint(__name__, 0, "test: {0}", ET.tostring(xml_combined))
        return ET.tostring(xml_combined)
        
           
       
if __name__=="__main__":
    dprint(__name__, 0, "Welcome to your class")
    #Plex = CPlexMgr('UDID')
    #test = Plex.myPlexLogin("USERNAME", "PASSWORD")
    #dprint(__name__, 0, "token: {0}", Plex.myplex_token)
    #Plex.discoverPMS()
    #Plex.discovermyPlex()
    #Plex = CPlexMgr.from_state('UDID')
    #Plex.getXML()
    #Plex.discovermyPlex()
    #Plex.discovermyPlex(True)
    #del Plex