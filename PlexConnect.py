#!/usr/bin/python

"""
PlexConnect

Sources:
inter-process-communication (queue): http://pymotw.com/2/multiprocessing/communication.html
"""


import sys
from multiprocessing import Process, Queue

import DNSServer, WebServer
import Settings



if __name__=="__main__":
    try:
        cmd_DNSServer = Queue()
        cmd_WebServer = Queue()
        
        p_DNSServer = Process(target=DNSServer.Run, args=(cmd_DNSServer,))
        p_DNSServer.start()
        
        p_WebServer = Process(target=WebServer.Run, args=(cmd_WebServer,))
        p_WebServer.start()
        
        print "***"
        print "PlexConnect"
        print "Press ENTER to shut down."
        print "***"
        key = raw_input()
    
    except KeyboardInterrupt:
        print "^C received."
    
    finally:
        print "PlexConnect: Shutting down."
        cmd_DNSServer.put('shutdown')
        cmd_WebServer.put('shutdown')
        
        p_DNSServer.join()
        p_WebServer.join()
