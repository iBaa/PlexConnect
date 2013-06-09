#!/usr/bin/python

"""
PlexConnect

Sources:
inter-process-communication (queue): http://pymotw.com/2/multiprocessing/communication.html
"""


import sys, time
import socket
from multiprocessing import Process, Queue

import PlexGDM
import DNSServer, WebServer
import Settings
from Debug import *  # dprint()


def getIP_self():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('1.2.3.4', 1000))
    IP = s.getsockname()[0]
    dprint('PlexConnect', 0, "IP_self: "+IP)
    return IP



if __name__=="__main__":
    dprint('PlexConnect', 0, "***")
    dprint('PlexConnect', 0, "PlexConnect")
    dprint('PlexConnect', 0, "Press ENTER to shut down.")
    dprint('PlexConnect', 0, "***")
    
    cfg = Settings.CSettings()
    
    if cfg.getSetting('enable_dnsserver')=='True':
        cmd_DNSServer = Queue()
    cmd_WebServer = Queue()
    
    param = {}
    param['IP_self'] = getIP_self()
    param['IP_DNSMaster'] = cfg.getSetting('ip_dnsmaster')
    param['HostToIntercept'] = 'trailers.apple.com'
    
    # default PMS
    param['IP_PMS'] = cfg.getSetting('ip_pms')
    param['Port_PMS'] = cfg.getSetting('port_pms')
    param['HTTP_IP'] = cfg.getSetting('http_ip')
    param['HTTP_Port'] = int(cfg.getSetting('http_port'))
    param['Addr_PMS'] = param['IP_PMS']+':'+param['Port_PMS']
    
    if cfg.getSetting('enable_plexgdm')=='True':
        if PlexGDM.Run()>0:
            param['IP_PMS'] = PlexGDM.getIP_PMS()
            param['Port_PMS'] = PlexGDM.getPort_PMS()
            param['Addr_PMS'] = param['IP_PMS']+':'+param['Port_PMS']
    
    dprint('PlexConnect', 0, "PMS: {0}", param['Addr_PMS'])
    
    if cfg.getSetting('enable_dnsserver')=='True':
        p_DNSServer = Process(target=DNSServer.Run, args=(cmd_DNSServer, param))
        p_DNSServer.start()
    
        time.sleep(0.1)
        if not p_DNSServer.is_alive():
            dprint('PlexConnect', 0, "DNSServer not alive. Shutting down.")
            sys.exit(1)
    
    p_WebServer = Process(target=WebServer.Run, args=(cmd_WebServer, param))
    p_WebServer.start()
    
    time.sleep(0.1)
    if not p_WebServer.is_alive():
        dprint('PlexConnect', 0, "WebServer not alive. Shutting down.")
        if cfg.getSetting('enable_dnsserver')=='True':
            cmd_DNSServer.put('shutdown')
            p_DNSServer.join()
        sys.exit(1)
    
    try:
        key = raw_input()
    except KeyboardInterrupt:
        dprint('PlexConnect', 0, "^C received.")
    
    finally:
        dprint('PlexConnect', 0,  "Shutting down.")
        if cfg.getSetting('enable_dnsserver')=='True':
            cmd_DNSServer.put('shutdown')
            p_DNSServer.join()
        
        cmd_WebServer.put('shutdown')
        p_WebServer.join()
