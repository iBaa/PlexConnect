#!/usr/bin/env python

"""
PlexConnect

Sources:
inter-process-communication (queue): http://pymotw.com/2/multiprocessing/communication.html
"""


import sys, time
from os import sep
import socket
import signal
from multiprocessing import Process, Pipe, active_children

import PlexGDM
import DNSServer, WebServer
import Settings
from Debug import *  # dprint()

pipe_WebServer = None
pipe_DNSServer = None

def getIP_self():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('1.2.3.4', 1000))
    IP = s.getsockname()[0]
    dprint('PlexConnect', 0, "IP_self: "+IP)
    return IP

def sig_handler(signum=None, frame=None):
    if type(signum) != type(None):
        dprint('PlexConnect', 0,  "Shutting down.")
        if pipe_DNSServer != None:
            pipe_DNSServer[0].send('shutdown')
        if pipe_DNSServer != None:
            pipe_WebServer[0].send('shutdown')


if __name__=="__main__":
    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)
    param = {}
    param['LogFile'] = sys.path[0] + sep + 'PlexConnect.log'
    dinit('PlexConnect', param, True)  # init logging, new file, main process

    dprint('PlexConnect', 0, "***")
    dprint('PlexConnect', 0, "PlexConnect")
    dprint('PlexConnect', 0, "Press ctrl-c to shut down.")
    dprint('PlexConnect', 0, "***")
    
    # Settings
    cfg = Settings.CSettings()
    param['CSettings'] = cfg
    
    param['IP_self'] = getIP_self()
    param['HostToIntercept'] = 'trailers.apple.com'
    
    # Logfile, re-init
    param['LogLevel'] = cfg.getSetting('loglevel')
    dinit('PlexConnect', param)  # re-init logfile with loglevel
    
    if cfg.getSetting('enable_dnsserver')=='True':
        pipe_DNSServer = Pipe()  # endpoint [0]-PlexConnect, [1]-DNSServer
    pipe_WebServer = Pipe()  # endpoint [0]-PlexConnect, [1]-WebServer
    
    # default PMS
    param['IP_PMS'] = cfg.getSetting('ip_pms')
    param['Port_PMS'] = cfg.getSetting('port_pms')
    param['Addr_PMS'] = param['IP_PMS']+':'+param['Port_PMS']
    
    if cfg.getSetting('enable_plexgdm')=='True':
        if PlexGDM.Run()>0:
            param['IP_PMS'] = PlexGDM.getIP_PMS()
            param['Port_PMS'] = PlexGDM.getPort_PMS()
            param['Addr_PMS'] = param['IP_PMS']+':'+param['Port_PMS']
    
    dprint('PlexConnect', 0, "PMS: {0}", param['Addr_PMS'])
    
    if cfg.getSetting('enable_dnsserver')=='True':
        p_DNSServer = Process(target=DNSServer.Run, args=(pipe_DNSServer[1], param))
        p_DNSServer.start()
    
        time.sleep(0.1)
        if not p_DNSServer.is_alive():
            dprint('PlexConnect', 0, "DNSServer not alive. Shutting down.")
            sys.exit(1)
    
    p_WebServer = Process(target=WebServer.Run, args=(pipe_WebServer[1], param))
    p_WebServer.start()
    
    time.sleep(0.1)
    if not p_WebServer.is_alive():
        dprint('PlexConnect', 0, "WebServer not alive. Shutting down.")
        if cfg.getSetting('enable_dnsserver')=='True':
            pipe_DNSServer[0].send('shutdown')
            p_DNSServer.join()
        sys.exit(1)
    
    # wait till processed are gone
    if cfg.getSetting('enable_dnsserver')=='True':
        p_DNSServer.join()
    
    p_WebServer.join()
