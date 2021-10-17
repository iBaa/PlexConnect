#!/usr/bin/env python

"""
PlexConnectDaemon

Creates a proper daemon on mac/linux
"""

import os
import sys
import signal
import argparse
import atexit
from PlexConnect import startup, shutdown, run, cmdShutdown
from contextlib import redirect_stderr, redirect_stdout


def daemonize(args):
    """
    do the UNIX double-fork magic, see Stevens' "Advanced
    Programming in the UNIX Environment" for details (ISBN 0201563177)
    """

    # Make a non-session-leader child process
    try:
        pid = os.fork()
        if pid != 0:
            sys.exit(0)
    except OSError as e:
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
    except OSError as e:
        raise RuntimeError("2nd fork failed: %s [%d]" % (e.strerror, e.errno))

    if args.pidfile:
        try:
            atexit.register(delpid)
            pid = str(os.getpid())
            with open(args.pidfile, 'w') as fh:
                fh.write(f"{pid}")
        except IOError as e:
            raise SystemExit(
                "Unable to write PID file: %s [%d]" % (e.strerror, e.errno))


def delpid():
    global args
    os.remove(args.pidfile)


def sighandler_shutdown(signum, frame):
    signal.signal(signal.SIGINT, signal.SIG_IGN)  # we heard you!
    cmdShutdown()


if __name__ == '__main__':
    signal.signal(signal.SIGINT, sighandler_shutdown)
    signal.signal(signal.SIGTERM, sighandler_shutdown)

    parser = argparse.ArgumentParser(description='PlexConnect as daemon.')
    parser.add_argument('--pidfile', dest='pidfile')
    args = parser.parse_args()

    with redirect_stdout(open(os.devnull, "a")):
        with redirect_stderr(open(os.devnull, "a")):
            daemonize(args)

            running = startup()

            while running:
                running = run()

            shutdown()
