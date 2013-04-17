#!/usr/bin/python

"""
Global Settings...
"""

# Plex Media Server
def getIP_PMS():
    return '192.168.178.20'  # todo: auto-discovery (Bonjour, GDM?)
def getPort_PMS():
    return 32400

# AppleTV/Client
def getIP_aTV():
    return '192.168.178.22'  # todo: how about more than one aTV?

def getIP_DNSmaster():  # Router, ISP's DNS, ...
    return '192.168.178.1'