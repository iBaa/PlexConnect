#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Movie Poster Screensaver functions
"""

try:
    import xml.etree.cElementTree as etree
except ImportError:
    import xml.etree.ElementTree as etree

import json

from Debug import *  # dprint(), prettyXML()
import PlexAPI
import Settings



"""
Plex Media Server: get movie posters, return to aTV as JSON list

parameters:
    PMS_address
    path
    options - dict() of PlexConnect-options as received from aTV, None for no std. X-Plex-Args
result:
    aTV screensaver JSON or 'False' in case of error
"""
def getScreensaverJSON(options):

    path = '/library/sections/1/recentlyAdded'
    
    if not 'PlexConnectUDID' in options:
        # aTV unidentified, UDID not known
        return False
    
    UDID = options['PlexConnectUDID']

    PlexAPI.discoverPMS(UDID, Settings.CSettings())

    # determine PMS_uuid, PMSBaseURL from IP (PMS_mark)
    PMS_uuid = PlexAPI.getPMSFromAddress(UDID, '')
    PMS_baseURL = PlexAPI.getPMSProperty(UDID, PMS_uuid, 'baseURL')

    # retrieve recently added movies from PMS
    xml = PlexAPI.getXMLFromPMS(PMS_baseURL, path)

    movies = []

    for video in xml.findall('Video'):
        movies.append({
            'title': video.get('title'),
            'thumb': video.get('thumb'),
        })

    ssPosters = []
    postersCount = 0
    for movie in movies:
        ssPosters.append({
           "type": "photo",
           "id": "photo_" + str(postersCount),
           "assets": [{
               "width": 406,
               "height": 600,
               "src": PMS_baseURL + movie['thumb'],
           }]
        })
        postersCount += 1

    if (len(ssPosters) > options['PlexConnectImagesLength']):
        JSON = json.dumps(ssPosters[0:options['PlexConnectImagesLength']])
    else:
        JSON = json.dumps(ssPosters)
    
    dprint(__name__, 1, "====== generated aTV Screensaver JSON ======")
    dprint(__name__, 1, "{0} [...]", JSON[:255])
    dprint(__name__, 1, "====== aTV Screensaver JSON finished ======")
    return(JSON)