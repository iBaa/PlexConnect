#!/usr/bin/env python

"""
PlexConnect

Sources:
inter-process-communication (queue): http://pymotw.com/2/multiprocessing/communication.html
"""


import sys, time
from os import sep
import socket
from multiprocessing import Process, Pipe
import signal

import DNSServer, WebServer
import Settings
from Debug import *  # dprint()



def getIP_self():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('1.2.3.4', 1000))
    IP = s.getsockname()[0]
    dprint('PlexConnect', 0, "IP_self: "+IP)
    return IP



g_shutdown = False

def sighandler_shutdown(signum, frame):
    dprint('PlexConnect', 0,  "Shutting down.")
    global g_shutdown
    g_shutdown = True
    if pipe_DNSServer != None:
        pipe_DNSServer[0].send('shutdown')
    if pipe_DNSServer != None:
        pipe_WebServer[0].send('shutdown')



if __name__=="__main__":
    signal.signal(signal.SIGINT, sighandler_shutdown)
    signal.signal(signal.SIGTERM, sighandler_shutdown)
    
    pipe_DNSServer = None
    pipe_WebServer = None
    
    param = {}
    param['LogFile'] = sys.path[0] + sep + 'PlexConnect.log'
    dinit('PlexConnect', param, True)  # init logging, new file, main process

    dprint('PlexConnect', 0, "***")
    dprint('PlexConnect', 0, "PlexConnect")
    dprint('PlexConnect', 0, "Press CTRL-C to shut down.")
    dprint('PlexConnect', 0, "***")
    
    # Settings
    cfg = Settings.CSettings()
    param['CSettings'] = cfg
    
    param['IP_self'] = getIP_self()
    param['HostToIntercept'] = 'trailers.apple.com'
    
    # Logfile, re-init
    param['LogLevel'] = cfg.getSetting('loglevel')
    dinit('PlexConnect', param)  # re-init logfile with loglevel
    
    # init DNSServer
    if cfg.getSetting('enable_dnsserver')=='True':
        pipe_DNSServer = Pipe()  # endpoint [0]-PlexConnect, [1]-DNSServer
        p_DNSServer = Process(target=DNSServer.Run, args=(pipe_DNSServer[1], param))
        p_DNSServer.start()
    
        time.sleep(0.1)
        if not p_DNSServer.is_alive():
            dprint('PlexConnect', 0, "DNSServer not alive. Shutting down.")
            sys.exit(1)
    
    # init WebServer
    pipe_WebServer = Pipe()  # endpoint [0]-PlexConnect, [1]-WebServer
    p_WebServer = Process(target=WebServer.Run, args=(pipe_WebServer[1], param))
    p_WebServer.start()
    
    time.sleep(0.1)
    if not p_WebServer.is_alive():
        dprint('PlexConnect', 0, "WebServer not alive. Shutting down.")
        if cfg.getSetting('enable_dnsserver')=='True':
            pipe_DNSServer[0].send('shutdown')
            p_DNSServer.join()
        sys.exit(1)
    
    # work until shutdown
    # ...or just wait until child processes are done
    # while g_shutdown==False:
    #     # do something important
    #     time.sleep(1)
    
    if cfg.getSetting('enable_dnsserver')=='True':
        p_DNSServer.join()
    
    p_WebServer.join()
