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
import errno
import getopt

import DNSServer
import WebServer
import Settings
from Debug import *  # dprint()


class PlexConnect(object):
    def __init__(self, *args, **kwargs):
        self.running = False
        self.logfile = sys.path[0] + os.sep + 'PlexConnect.log'
        self.pipes = []
        self.processes = []
        self.param = {}

     # override, call base and add your arguments letters to the string
    def get_arguments_short(self):
        return "l:"

    # override, call base and add your arguments to the list
    def get_arguments_long(self):
        return ['logfile=']

    # override, call base and add your arguments help text
    def get_arguments_declaration(self):
        return "[--logfile filename]"

    # parse the arguments
    def parse_arguments(self, args):
        try:
            opts, args = getopt.getopt(args, self.get_arguments_short(), self.get_arguments_long())  # @UnusedVariable
            self.handle_arguments(opts)
        except getopt.GetoptError:
            print ("Available Options:  %s" % self.get_arguments_declaration())
            sys.exit(0)

    # handle the arguments, override to handle your own parameters
    def handle_arguments(self, opts):
        for o, a in opts:
            if o in ('-l', '--logfile'):
                self.logfile = str(a)

    def getIP(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('1.2.3.4', 1000))
        IP = s.getsockname()[0]
        dprint('PlexConnect', 0, "IP_self: "+IP)
        return IP

    def stop(self):
        self.running = False
        # send shutdown to all pipes
        for pipe in self.pipes:
            pipe.send('shutdown')

    def cleanup(self):
        # join all processes
        for process in self.processes:
            process.join()
        dprint('PlexConnect', 0, "shutdown")

    # initialize the settings and startup all needed processes
    def start(self):
        # setup logfile location
        self.param['LogFile'] = self.logfile

        dinit('PlexConnect', self.param, True)  # init logging, new file, main process

        # Settings
        cfg = Settings.CSettings()
        self.param['CSettings'] = cfg

        self.param['IP_self'] = self.getIP()
        self.param['HostToIntercept'] = 'trailers.apple.com'

        # Logfile, re-init
        self.param['LogLevel'] = cfg.getSetting('loglevel')
        dinit('PlexConnect', self.param)  # re-init logfile with loglevel

        self.running = True

        if cfg.getSetting('enable_dnsserver') == 'True':
            sender, receiver = Pipe()  # endpoint [0]-PlexConnect, [1]-DNSServer
            process = Process(target=DNSServer.Run, args=(receiver, self.param))
            process.start()

            time.sleep(0.1)
            if not process.is_alive():
                dprint('PlexConnect', 0, "DNSServer not alive. Shutting down.")
                self.running = false
            else:
                self.pipes.append(sender)
                self.processes.append(process)

        if (self.running):
            # init WebServer
            sender, receiver = Pipe()  # endpoint [0]-PlexConnect, [1]-WebServer
            process = Process(target=WebServer.Run, args=(receiver, self.param))
            process.start()

            time.sleep(0.1)
            if not process.is_alive():
                dprint('PlexConnect', 0, "WebServer not alive. Shutting down.")
                self.running = false
            else:
                self.pipes.append(sender)
                self.processes.append(process)

        # not started successful, stop the parts that did start
        if (not self.running):
            self.stop()

        return self.running

    def loop(self):
        # do something important
        try:
            time.sleep(60)
        except IOError as e:
            if e.errno == errno.EINTR and not self.running:
                pass  # mask "IOError: [Errno 4] Interrupted function call"
            else:
                raise

    def run(self):
        while self.running:
            self.loop()


def sighandler_shutdown(signum, frame):
    signal.signal(signal.SIGINT, signal.SIG_IGN)  # we heard you!
    plexConnect.stop()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, sighandler_shutdown)
    signal.signal(signal.SIGTERM, sighandler_shutdown)

    plexConnect = PlexConnect()
    # configure the object based on the command line options
    plexConnect.parse_arguments(sys.argv[1:])

    dprint('PlexConnect', 0, "***")
    dprint('PlexConnect', 0, "PlexConnect")
    dprint('PlexConnect', 0, "Press CTRL-C to shut down.")
    dprint('PlexConnect', 0, "***")

    if (plexConnect.start()):
        plexConnect.run()

    plexConnect.cleanup()
    sys.exit(0)
