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

    def __init__(self):
        self.running = False
        self.logfile = sys.path[0] + os.sep + 'PlexConnect.log'
        self.pipes = []
        self.processes = []
        self.param = {}
        self.parse_opts(sys.argv[1:])

    def getIP(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('1.2.3.4', 1000))
        IP = s.getsockname()[0]
        dprint('PlexConnect', 0, "IP_self: " + IP)
        return IP

    def get_opts_short(self):
        """
        getopts short options
        override, call bass class and add your own short opts [string]
        """
        return "l:"

    def get_opts_long(self):
        """
        getopts long options
        override, call bass class and add your own long opts [list]
        """
        return ['logfile=']

    def get_opts_clarification(self):
        """
        getopts clarification
        override, call bass class and add your own clarification for opts [string]
        """
        return "[--logfile filename]"

    def parse_opts(self, args):
        """
        Parse the argumets passed onto the application
        """
        try:
            opts, args = getopt.getopt(args, self.get_opts_short(), self.get_opts_long())  # @UnusedVariable
            self.handle_opts(opts)
        except getopt.GetoptError:
            print("Available Options:  %s" % self.get_opts_clarification())
            sys.exit(0)

    def handle_opts(self, opts):
        """
        handle arguments
        override, call bass class and add your own argument handling
        """
        for o, a in opts:
            if o in ('-l', '--logfile'):
                self.logfile = str(a)

    def activate(self):
        """
        Main running sequence for a PlexConnect object
        """
        self.startup()
        self.run()
        self.shutdown()

    def request_shutdown(self):
        """
        request_shutdown will initiate a shutdown of  PlexConnect by sending all processes a 'shutdown' request
        but it does not wait till everything is down
        """
        self.running = False
        # send shutdown to all pipes
        for pipe in self.pipes:
            pipe.send('shutdown')

    def shutdown(self):
        """
        shutdown wait till PlexConnect brought everything down
        when no request_shutdown was sent yet it will do that first
        """
        if  (self.running):
            self.request_shutdown()
        # join all processes
        for process in self.processes:
            process.join()
        dprint('PlexConnect', 0, "shutdown")

    # initialize the settings and startup all needed processes
    def startup(self):
        """
        Startup PlexConnect
        """
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

        # not started successful
        if (not self.running):
            # shutdown the parts that did start
            self.shutdown()
            sys.exit(1)

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
    plexConnect.request_shutdown()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, sighandler_shutdown)
    signal.signal(signal.SIGTERM, sighandler_shutdown)

    plexConnect = PlexConnect()

    # write out some help text
    dprint('PlexConnect', 0, "***")
    dprint('PlexConnect', 0, "PlexConnect")
    dprint('PlexConnect', 0, "Press CTRL-C to shut down.")
    dprint('PlexConnect', 0, "***")

    plexConnect.activate()

    sys.exit(0)
