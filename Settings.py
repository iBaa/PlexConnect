#!/usr/bin/python

"""
Global Settings...
"""

# Plex Media Server
def getIP_PMS():
    return '192.168.0.200'  # todo: auto-discovery (Bonjour, GDM?)
def getPort_PMS():
    return 32400

# AppleTV/Client
def getIP_aTV():
    return '192.168.0.8'  # todo: how about more than one aTV?

def getIP_DNSmaster():  # Router, ISP's DNS, ...
    return '194.168.4.100'