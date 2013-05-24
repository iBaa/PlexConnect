#!/usr/bin/python
from Debug import *  # dprint()
"""
Global Settings...
"""

settingsMovieView = 'Movie_Grid.xml'
settingsShowView = 'Show_List.xml'
settingsForceDirectPlay = False
settingsForceTranscode = False

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
    return settingsForceDirectPlay

def getForceTranscoding():
    return settingsForceTranscode
    
def getMovieViewType():
    return settingsMovieView
       
def getShowViewType():
    return settingsShowView
        
def updateSettings(setting):
    #print('ATVLogger', 0, setting)
    #dprint('ATVLogger', 0, value)
    global settingsMovieView
    global settingsShowView
    global settingsForceDirectPlay
    global settingsForceTranscode
    
    dprint('ATVLogger', 0, setting)
    parts = setting.split(':')
    
    for i in range(0, len(parts)):
      dprint('ATVLogger', 0, parts[i])
      if parts[i] == 'MovieView':
        if parts[i+1] == 'Grid': settingsMovieView = 'Movie_Grid.xml'
        if parts[i+1] == 'List': settingsMovieView = 'Movie_List.xml'
        
      if parts[i] == 'ShowView':
        if parts[i+1] == 'Grid': settingsShowView = 'Show_Grid.xml'
        if parts[i+1] == 'List': settingsShowView = 'Show_List.xml'
    
    return
