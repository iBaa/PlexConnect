#!/usr/bin/python

"""
Global Settings...
"""

#
# Plex Media Server
def getPlexGDM():
    return True  # True: use PlexGDM (GoodDayMate) to auto discover PMS

def getIP_PMS():  # default IP, if GDM fails... todo: do we need this fall back?
    return '192.168.178.2'
def getPort_PMS():
    return 32400

#
# DNS/WebServer
def getIP_DNSmaster():  # Router, ISP's DNS, ...
    return '8.8.8.8'  # google public DNS

def getHostToIntercept():
    return 'trailers.apple.com'

#
# AppleTV
def getForceDirectPlay():  # if true, this has higher priority than transcoding
    return False

def getForceTranscoding():
    return False