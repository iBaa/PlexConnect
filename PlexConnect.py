#!/usr/bin/env python

"""
PlexConnect

Sources:
inter-process-communication (queue): http://pymotw.com/2/multiprocessing/communication.html
"""


import sys
import time
import os
import socket
from multiprocessing import Process, Pipe
import signal
import  errno
import signal
import getopt

import DNSServer
import WebServer
import Settings
from Debug import *  # dprint()


g_pipes = []
g_processes = []
g_shutdown = False
g_createpid = False
g_pidfile = None
g_daemon = None


def getIP_self():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('1.2.3.4', 1000))
    IP = s.getsockname()[0]
    dprint('PlexConnect', 0, "IP_self: "+IP)
    return IP


def shutdown(code):
    # join all processes
    for process in g_processes:
        process.join()
    dprint('PlexConnect', 0, "shutdown")
    #remove pid file if any
    if g_createpid:
        os.remove(g_pidfile)
    if (code):
        sys.exit(code)


def request_shutdown():
    dprint('PlexConnect', 0,  "Shutting down.")
    global g_shutdown
    g_shutdown = True
    # send shutdown to all pipes
    for pipe in g_pipes:
        pipe.send('shutdown')


def sighandler_shutdown(signum, frame):
    request_shutdown()


def daemonize():
    """
    do the UNIX double-fork magic, see Stevens' "Advanced
    Programming in the UNIX Environment" for details (ISBN 0201563177)
    """
    dprint('PlexConnect', 0,  "Starting deamon.")

    # Make a non-session-leader child process
    try:
        pid = os.fork()  # @UndefinedVariable - only available in UNIX
        if pid != 0:
            sys.exit(0)
    except OSError, e:
        raise RuntimeError("1st fork failed: %s [%d]" % (e.strerror, e.errno))

    # decouple from parent environment
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

    # redirect standard file descriptors
    dev_null = file('/dev/null', 'r')
    sys.stdout.flush()
    sys.stderr.flush()
    os.dup2(dev_null.fileno(), sys.stdin.fileno())
    os.dup2(dev_null.fileno(), sys.stdout.fileno())
    os.dup2(dev_null.fileno(), sys.stderr.fileno())

    global g_createpid, g_createpid
    if g_createpid:
        pid = str(os.getpid())
        dprint('PlexConnect', 0, "Writing PID " + pid + " to " + str(g_pidfile))
        file(g_pidfile, 'w').write("%s\n" % pid)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, sighandler_shutdown)
    signal.signal(signal.SIGTERM, sighandler_shutdown)

    param = {}
    param['LogFile'] = sys.path[0] + os.sep + 'PlexConnect.log'
    dinit('PlexConnect', param, True)  # init logging, new file, main process

    # Settings
    cfg = Settings.CSettings()
    param['CSettings'] = cfg

    param['IP_self'] = getIP_self()
    param['HostToIntercept'] = 'trailers.apple.com'

    # Logfile, re-init
    param['LogLevel'] = cfg.getSetting('loglevel')
    dinit('PlexConnect', param)  # re-init logfile with loglevel

    try:
        opts, args = getopt.getopt(sys.argv[1:], "dp:", ['daemon', 'pidfile='])  # @UnusedVariable
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
    else:
        dprint('PlexConnect', 0, "***")
        dprint('PlexConnect', 0, "PlexConnect")
        dprint('PlexConnect', 0, "Press CTRL-C to shut down.")
        dprint('PlexConnect', 0, "***")

    # init DNSServer
    if cfg.getSetting('enable_dnsserver') == 'True':
        sender, receiver = Pipe()  # endpoint [0]-PlexConnect, [1]-DNSServer
        process = Process(target=DNSServer.Run, args=(receiver, param))
        process.start()

        time.sleep(0.1)
        if not process.is_alive():
            dprint('PlexConnect', 0, "DNSServer not alive. Shutting down.")
            request_shutdown()
            shutdown(1)
        g_pipes.append(sender)
        g_processes.append(process)

    # init WebServer
    sender, receiver = Pipe()  # endpoint [0]-PlexConnect, [1]-WebServer
    process = Process(target=WebServer.Run, args=(receiver, param))
    process.start()

    time.sleep(0.1)
    if not process.is_alive():
        dprint('PlexConnect', 0, "WebServer not alive. Shutting down.")
        request_shutdown()
        shutdown(1)
    g_pipes.append(sender)
    g_processes.append(process)

    # work until shutdown
    # ...or just wait until child processes are done
    if sys.platform == 'win32':
        while not g_shutdown:
            # do something important
            try:
                time.sleep(60)
            except IOError as e:
                if e.errno == errno.EINTR and g_shutdown == True:
                    pass  # mask "IOError: [Errno 4] Interrupted function call"
                else:
                    raise

    shutdown(0)
