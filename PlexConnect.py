#!/usr/bin/python

"""
PlexConnect
"""


import sys
from multiprocessing import Process

import DNSServer, WebServer
import Settings



if __name__=="__main__":
    try:
        DNSServer.SetKeepRunning(True)
        p_DNSServer = Process(target=DNSServer.Run)
        p_DNSServer.start()
        WebServer.SetKeepRunning(True)
        p_WebServer = Process(target=WebServer.Run)
        p_WebServer.start()
        
        while True:
            pass  # do something: GUI,...
    
    # todo: a nice shutdown
    except KeyboardInterrupt:
        print "PlexConnect: Shutting down."
        DNSServer.KeepRunning(False)
        WebServer.KeepRunning(False)
        
        p_DNSServer.join()
        p_WebServer.join()