#!/usr/bin/env python

"""
PlexConnect

Sources:
inter-process-communication (queue): http://pymotw.com/2/multiprocessing/communication.html
"""


import sys, time
import os
import socket
from multiprocessing import Process, Pipe
import signal
import getopt

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
g_createpid = False
g_pidfile = None
g_daemon = None


def shutdown():
    if p_DNSServer != None:
        p_DNSServer.join()
    if p_WebServer != None:
        p_WebServer.join()
    if g_createpid:
        dprint('PlexConnect', 0, "Removing pidfile")
        os.remove(g_pidfile)


def request_shutdown():
    dprint('PlexConnect', 0,  "Shutting down.")
    global g_shutdown
    g_shutdown = True
    if pipe_DNSServer != None:
        pipe_DNSServer[0].send('shutdown')
    if pipe_WebServer != None:
        pipe_WebServer[0].send('shutdown')
        

def sighandler_shutdown(signum, frame):
    request_shutdown();


def daemonize():
    """
    Fork off as a daemon
    """
    dprint('PlexConnect', 0,  "Starting deamon.")

    # pylint: disable=E1101
    # Make a non-session-leader child process
    try:
        pid = os.fork()  # @UndefinedVariable - only available in UNIX
        if pid != 0:
            sys.exit(0)
    except OSError, e:
        raise RuntimeError("1st fork failed: %s [%d]" % (e.strerror, e.errno))

    os.setsid()  # @UndefinedVariable - only available in UNIX

    # Make sure I can read my own files and shut out others
    prev = os.umask(0)
    os.umask(prev and int('077', 8))

    # Make the child a session-leader by detaching from the terminal
    try:
        pid = os.fork()  # @UndefinedVariable - only available in UNIX
        if pid != 0:
            sys.exit(0)
    except OSError, e:
        raise RuntimeError("2nd fork failed: %s [%d]" % (e.strerror, e.errno))

    dev_null = file('/dev/null', 'r')
    os.dup2(dev_null.fileno(), sys.stdin.fileno())

    global g_createpid, g_createpid
    if g_createpid:
        pid = str(os.getpid())
        dprint('PlexConnect', 0, "Writing PID " + pid + " to " + str(g_pidfile))
        file(g_pidfile, 'w').write("%s\n" % pid)


if __name__=="__main__":
    signal.signal(signal.SIGINT, sighandler_shutdown)
    signal.signal(signal.SIGTERM, sighandler_shutdown)
    
    pipe_DNSServer = None
    pipe_WebServer = None
    p_DNSServer = None
    p_WebServer = None
    
    param = {}
    param['LogFile'] = sys.path[0] + os.sep + 'PlexConnect.log'
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
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], "dp:", [ 'daemon', 'pidfile='])  # @UnusedVariable
    except getopt.GetoptError:
        dprint('PlexConnect', 0, "Available Options:  --daemon, --pidfile filename")
        sys.exit()
        
    for o, a in opts:
        #dprint('PlexConnect', 0,  "Options: %s Value: %s" % (o, a))
        # Run as a daemon
        if o in ('-d', '--daemon'):
            if sys.platform == 'win32':
                dprint('PlexConnect', 0, "Daemonize not supported under Windows, starting normally")
            else:
                g_daemon = True

        # Write a pidfile if requested
        if o in ('-p', '--pidfile'):
            g_pidfile = str(a)

            # If the pidfile already exists, PlexConnect may still be running, so exit
            if os.path.exists(g_pidfile):
                sys.exit("PID file '" + g_pidfile + "' already exists. Exiting.")

            # The pidfile is only useful in daemon mode, make sure we can write the file properly
            if g_daemon:
                g_createpid = True
                try:
                    file(g_pidfile, 'w').write("pid\n")
                except IOError, e:
                    raise SystemExit("Unable to write PID file: %s [%d]" % (e.strerror, e.errno))
            else:
                dprint('PlexConnect', 0, "Not running in daemon mode. PID file creation disabled")
                
    if g_daemon:
        daemonize()

    # init DNSServer
    if cfg.getSetting('enable_dnsserver')=='True':
        pipe_DNSServer = Pipe()  # endpoint [0]-PlexConnect, [1]-DNSServer
        p_DNSServer = Process(target=DNSServer.Run, args=(pipe_DNSServer[1], param))
        p_DNSServer.start()
    
        time.sleep(0.1)
        if not p_DNSServer.is_alive():
            dprint('PlexConnect', 0, "DNSServer not alive. Shutting down.")
            p_DNSServer = None;
            request_shutdown()
            shutdown()
            sys.exit(1)
    
    # init WebServer
    pipe_WebServer = Pipe()  # endpoint [0]-PlexConnect, [1]-WebServer
    p_WebServer = Process(target=WebServer.Run, args=(pipe_WebServer[1], param))
    p_WebServer.start()
    
    time.sleep(0.1)
    if not p_WebServer.is_alive():
        dprint('PlexConnect', 0, "WebServer not alive. Shutting down.")
        p_WebServer = None;
        request_shutdown()
        shutdown()
        sys.exit(1)
    
    # work until shutdown
    # ...or just wait until child processes are done
    if sys.platform == 'win32':
        while g_shutdown==False:
            # do something important
            try: 
                time.sleep(1)
            except IOError:
                dprint('PlexConnect', 0, "sleep aborted.") 
    
    shutdown()