#!/usr/bin/python

"""
loosely based on hippojay's plexGDM:
https://github.com/hippojay/plugin.video.plexbmc
"""



import sys
import struct
import httplib, socket

from Debug import *  # dprint()



PMS_list = []

IP_PlexGDM = '239.0.0.250'
Port_PlexGDM = 32414
Msg_PlexGDM = 'M-SEARCH * HTTP/1.0'



def getIP_PMS():
    # todo: currently only one server - return first entry
    if len(PMS_list)>0:
        return PMS_list[0]['server']
    else:
        return '127.0.0.1'

def getPort_PMS():
    # todo: currently only one server - return first entry
    if len(PMS_list)>0:
        return PMS_list[0]['port']
    else:
        return '32400'



def Run():
    
    dprint(__name__, 0, "***")
    dprint(__name__, 0, "looking up Plex Media Server")
    dprint(__name__, 0, "***")
    
    client_register_group = (IP_PlexGDM, 32413)
    client_update_port = 32412
    
    # setup socket for discovery -> multicast message
    GDM = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    GDM.settimeout(1.0)
    
    # Set the time-to-live for messages to 1 for local network
    GDM.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack('b', 1))
    
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

    global PMS_list
    PMS_list = []
    if returnData:
        for response in returnData:
            update = { 'server' : response.get('from')[0] }
            
            # Check if we had a positive HTTP response                        
            if "200 OK" in response.get('data'):
                for each in response.get('data').split('\n'): 
                    # decode response data
                    update['discovery'] = "auto"
                    update['owned']='1'
                    update['master']= 1
                    update['role']='master'
                    
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
            
            PMS_list.append(update)
    
    if PMS_list==[]:
        dprint(__name__, 0, "No servers discovered")
    else:
        dprint(__name__, 0, "servers discovered: {0}", len(PMS_list))
        for items in PMS_list:
            dprint(__name__, 1, "{0} {1}:{2}", items['serverName'], items['server'], items['port'])
    
    return len(PMS_list)



if __name__ == '__main__':
   Run()
   
   print "IP:", getIP_PMS()
   print "Port:", getPort_PMS()