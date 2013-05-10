#!/usr/bin/python

"""
PlexConnect

Sources:
inter-process-communication (queue): http://pymotw.com/2/multiprocessing/communication.html
"""


import sys
from multiprocessing import Process, Queue

import PlexGDM
import DNSServer, WebServer
import Settings
from Debug import *  # dprint()



if __name__=="__main__":
    try:
        dprint('PlexConnect', 0, "***")
        dprint('PlexConnect', 0, "PlexConnect")
        dprint('PlexConnect', 0, "Press ENTER to shut down.")
        dprint('PlexConnect', 0, "***")
        
        cmd_DNSServer = Queue()
        cmd_WebServer = Queue()
        
        PlexGDM.Run()
        
        p_DNSServer = Process(target=DNSServer.Run, args=(cmd_DNSServer,))
        p_DNSServer.start()
        
        p_WebServer = Process(target=WebServer.Run, args=(cmd_WebServer,))
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
