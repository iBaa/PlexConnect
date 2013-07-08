#!/usr/bin/env python

"""
PlexConnect

Sources:
inter-process-communication (queue): http://pymotw.com/2/multiprocessing/communication.html
"""


import sys
import os
import signal

from PlexConnect import PlexConnect
from Debug import *  # dprint()


class PlexConnectDaemon(PlexConnect):

    def __init__(self, *args, **kwargs):
        self.deamon = True
        self.createpid = False
        self.pidfile = None
        super(PlexConnectDaemon, self).__init__(*args, **kwargs)

    def get_arguments_short(self):
        return super(PlexConnectDaemon, self).get_arguments_short() + "dp:"

    def get_arguments_long(self):
        return super(PlexConnectDaemon, self).get_arguments_long() + ['pidfile=']

    def get_arguments_declaration(self):
        return super(PlexConnectDaemon, self).get_arguments_declaration() + " [--pidfile filename]"

    # handle the arguments, override to handle your own parameters
    def handle_arguments(self, opts):
        for o, a in opts:
            # Write a pidfile if requested
            if o in ('-p', '--pidfile'):
                self.pidfile = str(a)

                # If the pidfile already exists, PlexConnect may still be running, so exit
                if os.path.exists(self.pidfile):
                    sys.exit("PID file '" + self.pidfile + "' already exists. Exiting.")

                # The pidfile is only useful in daemon mode, make sure we can write the file properly
                if self.deamon:
                    self.createpid = True
                    try:
                        file(self.pidfile, 'w').write("pid\n")
                    except IOError, e:
                        raise SystemExit("Unable to write PID file: %s [%d]" % (e.strerror, e.errno))
                else:
                    print("Not running in daemon mode. PID file creation disabled")

    # do the UNIX double-fork magic, see Stevens' "Advanced
    # Programming in the UNIX Environment" for details (ISBN 0201563177)
    def daemonize(self):
        dprint('PlexConnect', 0,  "Starting deamon.")

        # Make a non-session-leader child process
        try:
            pid = os.fork()
            if pid != 0:
                sys.exit(0)
        except OSError, e:
            raise RuntimeError("1st fork failed: %s [%d]" % (e.strerror, e.errno))

        # decouple from parent environment
        os.setsid()

        # Make sure I can read my own files and shut out others
        prev = os.umask(0)
        os.umask(prev and int('077', 8))

        # Make the child a session-leader by detaching from the terminal
        try:
            pid = os.fork()
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

        if self.createpid:
            pid = str(os.getpid())
            dprint('PlexConnect', 0, "Writing PID " + pid + " to " + str(self.pidfile))
            file(self.pidfile, 'w').write("%s\n" % pid)

    def cleanup(self):
        super(PlexConnectDaemon, self).cleanup()
        #remove pid file if any
        if self.createpid:
            os.remove(self.pidfile)

    # daemonize if needed
    def handle_daemonizing(self):
        if (self.deamon):
            self.daemonize()


def sighandler_shutdown(signum, frame):
    signal.signal(signal.SIGINT, signal.SIG_IGN)  # we heard you!
    plexConnect.stop()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, sighandler_shutdown)
    signal.signal(signal.SIGTERM, sighandler_shutdown)

    plexConnect = PlexConnectDaemon()

    # configure the object based on the command line options
    plexConnect.parse_arguments(sys.argv[1:])

    plexConnect.handle_daemonizing()

    if (plexConnect.start()):
        plexConnect.run()

    plexConnect.cleanup()
    sys.exit(0)
