#!/usr/bin/python

"""
PlexConnect

Sources:
inter-process-communication (queue): http://pymotw.com/2/multiprocessing/communication.html
"""


import sys, time, os, signal
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

def daemonize():
    try:
        pid = os.fork()
        print pid
        if pid != 0:
            sys.exit(0)
            pass
    except OSError, e:
        raise RuntimeError("Fork failed: %s [%d]" % (e.strerror, e.errno))

    os.chdir("/")
    os.setsid()
    os.umask(0)
    
    try:
        pid = os.fork()
        print pid
        if pid != 0:
            sys.exit(0)
            pass
    except OSError, e:
        raise RuntimeError("Fork failed: %s [%d]" % (e.strerror, e.errno))

    # TODO: Write the pid to a file.


if __name__=="__main__":
    daemon = '-d' in sys.argv or '--daemon' in sys.argv
    if daemon and sys.platform is 'win32':
        dprint('PlexConnect', 0, "Running PlexConnect as a daemon is not supported on Windows.")
        daemon = False
    
    if daemon:
        # TODO: Would be good to have some logging here instead.
        sys.stdin = open('/dev/null','r')
        sys.stdout = open('/dev/null','w')
        sys.stderr = open('/dev/null','w')
        daemonize()    

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
    
    time.sleep(0.1)
    if not p_DNSServer.is_alive():
        dprint('PlexConnect', 0, "DNSServer not alive. Shutting down.")
        sys.exit(1)
    
    p_WebServer = Process(target=WebServer.Run, args=(cmd_WebServer, param))
    p_WebServer.start()
    
    time.sleep(0.1)
    if not p_WebServer.is_alive():
        dprint('PlexConnect', 0, "WebServer not alive. Shutting down.")
        cmd_DNSServer.put('shutdown')
        p_DNSServer.join()
        sys.exit(1)
    
    def signal_handler(signal, frame):
        dprint('PlexConnect', 0, "PlexConnect caught shutdown signal. Shutting down.")
        cmd_DNSServer.put('shutdown')
        cmd_WebServer.put('shutdown')

        p_DNSServer.join()
        p_WebServer.join()

        sys.exit(0)

    if daemon:
        signal.signal(signal.SIGTERM, signal_handler)
        signal.pause()
    else:
        try:
            key = raw_input()
        except KeyboardInterrupt:
            dprint('PlexConnect', 0, "^C received.")
        
        finally:
            dprint('PlexConnect', 0,  "Shutting down.")
            cmd_DNSServer.put('shutdown')
            cmd_WebServer.put('shutdown')
            
            p_DNSServer.join()
            p_WebServer.join()
