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
import signal, errno

import DNSServer, WebServer
import Settings
from Debug import *  # dprint()



def getIP_self():
    IP = socket.gethostbyname(socket.gethostname())
    if IP.startswith('127.'):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('1.2.3.4', 1000))
        IP = s.getsockname()[0]
    dprint('PlexConnect', 0, "IP_self: "+IP)
    return IP



procs = {}
pipes = {}
param = {}
running = False

def startup():
    global procs
    global pipes
    global param
    global running
    
    # Settings
    cfg = Settings.CSettings()
    param['CSettings'] = cfg
    
    # Logfile
    if cfg.getSetting('logpath').startswith('.'):
        # relative to current path
        logpath = sys.path[0] + sep + cfg.getSetting('logpath')
    else:
        # absolute path
        logpath = cfg.getSetting('logpath')
    
    param['LogFile'] = logpath + sep + 'PlexConnect.log'
    param['LogLevel'] = cfg.getSetting('loglevel')
    dinit('PlexConnect', param, True)  # init logging, new file, main process
    
    # more Settings
    param['IP_self'] = getIP_self()
    param['HostToIntercept'] = 'trailers.apple.com'
    
    running = True
    
    # init DNSServer
    if cfg.getSetting('enable_dnsserver')=='True':
        master, slave = Pipe()  # endpoint [0]-PlexConnect, [1]-DNSServer
        proc = Process(target=DNSServer.Run, args=(slave, param))
        proc.start()
        
        time.sleep(0.1)
        if proc.is_alive():
            procs['DNSServer'] = proc
            pipes['DNSServer'] = master
        else:
            dprint('PlexConnect', 0, "DNSServer not alive. Shutting down.")
            running = False
    
    # init WebServer
    if running:
        master, slave = Pipe()  # endpoint [0]-PlexConnect, [1]-WebServer
        proc = Process(target=WebServer.Run, args=(slave, param))
        proc.start()
        
        time.sleep(0.1)
        if proc.is_alive():
            procs['WebServer'] = proc
            pipes['WebServer'] = master
        else:
            dprint('PlexConnect', 0, "WebServer not alive. Shutting down.")
            running = False
    
    # not started successful - clean up
    if not running:
        cmdShutdown()
        shutdown()
        sys.exit(1)

def run():
    while running:
        # do something important
        try:
            time.sleep(60)
        except IOError as e:
            if e.errno == errno.EINTR and not running:
                pass  # mask "IOError: [Errno 4] Interrupted function call"
            else:
                raise

def shutdown():
    for slave in procs:
        procs[slave].join()
    dprint('PlexConnect', 0, "shutdown")

def cmdShutdown():
    global running
    running = False
    # send shutdown to all pipes
    for slave in pipes:
        pipes[slave].send('shutdown')
    dprint('PlexConnect', 0, "Shutting down.")



def sighandler_shutdown(signum, frame):
    signal.signal(signal.SIGINT, signal.SIG_IGN)  # we heard you!
    cmdShutdown()



if __name__=="__main__":
    signal.signal(signal.SIGINT, sighandler_shutdown)
    signal.signal(signal.SIGTERM, sighandler_shutdown)
    
    dprint('PlexConnect', 0, "***")
    dprint('PlexConnect', 0, "PlexConnect")
    dprint('PlexConnect', 0, "Press CTRL-C to shut down.")
    dprint('PlexConnect', 0, "***")
    
    startup()
    
    run()
    
    shutdown()
