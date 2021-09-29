#!/usr/bin/env python

"""
PlexConnect

Sources:
inter-process-communication (queue): http://pymotw.com/2/multiprocessing/communication.html
"""


import sys
import time
from os import sep
import socket
from multiprocessing import Process, Pipe
from multiprocessing.managers import BaseManager
import signal
import errno
import argparse

from Version import __VERSION__
import DNSServer
import WebServer
import Settings
import ATVSettings
from PILBackgrounds import isPILinstalled
from Debug import *  # dprint()


CONFIG_PATH = '.'


def getIP_self():
    cfg = param['CSettings']
    if cfg.getSetting('enable_plexgdm') == 'False':
        dprint('PlexConnect', 0, f"IP_PMS: {cfg.getSetting('ip_pms')}")
    if cfg.getSetting('enable_plexconnect_autodetect') == 'True':
        # get public ip of machine running PlexConnect
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('1.2.3.4', 1000))
        IP = s.getsockname()[0]
        dprint('PlexConnect', 0, f"IP_self: {IP}")
    else:
        # manual override from "settings.cfg"
        IP = cfg.getSetting('ip_plexconnect')
        dprint('PlexConnect', 0, f"IP_self (from settings): {IP}")

    return IP


# initializer for Manager, proxy-ing ATVSettings to WebServer/XMLConverter
def initProxy():
    signal.signal(signal.SIGINT, signal.SIG_IGN)


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
    cfg = Settings.CSettings(CONFIG_PATH)
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

    dprint('PlexConnect', 0, "Version: {0}", __VERSION__)
    dprint('PlexConnect', 0, "Python: {0}", sys.version)
    dprint('PlexConnect', 0, "Host OS: {0}", sys.platform)
    dprint('PlexConnect', 0,
           "PILBackgrounds: Is PIL installed? {0}", isPILinstalled())

    # more Settings
    param['IP_self'] = getIP_self()
    param['HostToIntercept'] = cfg.getSetting('hosttointercept')
    param['baseURL'] = 'http://' + param['HostToIntercept']

    # proxy for ATVSettings
    proxy = BaseManager()
    proxy.register('ATVSettings', ATVSettings.CATVSettings)
    proxy.start(initProxy)
    param['CATVSettings'] = proxy.ATVSettings(CONFIG_PATH)
    running = True

    # init DNSServer
    if cfg.getSetting('enable_dnsserver') == 'True':
        dnsserver = DNSServer.DNSServer(param)
        dnsserver.start_thread()
        # if not dnsserver.isAlive():
        #     dprint('PlexConnect', 0, "DNSServer not alive. Shutting down.")
        #     running = False

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

    # init WebServer_SSL
    if running and \
       cfg.getSetting('enable_webserver_ssl') == 'True':
        master, slave = Pipe()  # endpoint [0]-PlexConnect, [1]-WebServer
        proc = Process(target=WebServer.Run_SSL, args=(slave, param))
        proc.start()

        time.sleep(0.1)
        if proc.is_alive():
            procs['WebServer_SSL'] = proc
            pipes['WebServer_SSL'] = master
        else:
            dprint('PlexConnect', 0, "WebServer_SSL not alive. Shutting down.")
            running = False

    # not started successful - clean up
    if not running:
        cmdShutdown()
        shutdown()

    return running


def run(timeout=60):
    # do something important
    try:
        time.sleep(timeout)
    except IOError as e:
        if e.errno == errno.EINTR and not running:
            pass  # mask "IOError: [Errno 4] Interrupted function call"
        else:
            raise

    return running


def shutdown():
    for slave in procs:
        procs[slave].join()
    if param['CATVSettings'].getSetting('enable_dnsserver') == 'True':
        if dnsserver:
            dnsserver.stop()
    param['CATVSettings'].saveSettings()

    dprint('PlexConnect', 0, "Shutdown")


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


if __name__ == "__main__":
    signal.signal(signal.SIGINT, sighandler_shutdown)
    signal.signal(signal.SIGTERM, sighandler_shutdown)
    parser = argparse.ArgumentParser()
    parser.add_argument('--config_path', metavar='<config_path>', required=False,
                        help='path of folder containing config files, relative to PlexConnect.py')
    args = parser.parse_args()
    if args.config_path:
        CONFIG_PATH = args.config_path

    dprint('PlexConnect', 0, "***")
    dprint('PlexConnect', 0, "PlexConnect")
    dprint('PlexConnect', 0, "Press CTRL-C to shut down.")
    dprint('PlexConnect', 0, "***")

    running = startup()

    while running:
        running = run()

    shutdown()
