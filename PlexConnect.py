#!/usr/bin/python

"""
PlexConnect

Sources:
inter-process-communication (queue): http://pymotw.com/2/multiprocessing/communication.html
"""


import sys
import socket
from multiprocessing import Process, Queue

import PlexGDM
import DNSServer, WebServer
import Settings
from Debug import *  # dprint()



def getIP_self():
    return socket.gethostbyname(socket.getfqdn())



if __name__=="__main__":
    try:
        dprint('PlexConnect', 0, "***")
        dprint('PlexConnect', 0, "PlexConnect")
        dprint('PlexConnect', 0, "Press ENTER to shut down.")
        dprint('PlexConnect', 0, "***")
        
        cmd_DNSServer = Queue()
        cmd_WebServer = Queue()
        
        param = {}
        param['IP_self'] = getIP_self()
        
        if Settings.getPlexGDM()==True:
            PlexGDM.Run()
            
            param['IP_PMS'] = PlexGDM.getIP_PMS()
            param['Port_PMS'] = PlexGDM.getPort_PMS()
            param['Addr_PMS'] = PlexGDM.getIP_PMS()+':'+str(PlexGDM.getPort_PMS())
        else:
            param['IP_PMS'] = Settings.getIP_PMS()
            param['Port_PMS'] = Settings.getPort_PMS()
            param['Addr_PMS'] = Settings.getIP_PMS()+':'+str(Settings.getPort_PMS())
        
        p_DNSServer = Process(target=DNSServer.Run, args=(cmd_DNSServer, param))
        p_DNSServer.start()
        
        p_WebServer = Process(target=WebServer.Run, args=(cmd_WebServer, param))
        p_WebServer.start()
        
        key = raw_input()
    
    except KeyboardInterrupt:
        print "^C received."
    
    finally:
        dprint('PlexConnect', 0,  "Shutting down.")
        cmd_DNSServer.put('shutdown')
        cmd_WebServer.put('shutdown')
        
        p_DNSServer.join()
        p_WebServer.join()
