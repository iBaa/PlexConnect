#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Subtitle transcoder functions
"""



import re
import urllib2
import json

from Debug import *  # dprint(), prettyXML()
import PlexAPI



"""
Plex Media Server: get subtitle, return as aTV subtitle JSON

parameters:
    PMS_address
    path
    options - dict() of PlexConnect-options as received from aTV, None for no std. X-Plex-Args
result:
    aTV subtitle JSON or 'False' in case of error
"""
def getSubtitleJSON(PMS_address, path, options):
    """
    # double check aTV UDID, redo from client IP if needed/possible
    if not 'PlexConnectUDID' in options:
        UDID = getATVFromIP(options['aTVAddress'])
        if UDID:
            options['PlexConnectUDID'] = UDID
    """
    path = path + '?' if not '?' in path else '&'
    path = path + 'encoding=utf-8'
    
    if not 'PlexConnectUDID' in options:
        # aTV unidentified, UDID not known
        return False
    
    UDID = options['PlexConnectUDID']
    
    # determine PMS_uuid, PMSBaseURL from IP (PMS_mark)
    xargs = {}
    PMS_uuid = PlexAPI.getPMSFromAddress(UDID, PMS_address)
    PMS_baseURL = PlexAPI.getPMSProperty(UDID, PMS_uuid, 'baseURL')
    xargs['X-Plex-Token'] = PlexAPI.getPMSProperty(UDID, PMS_uuid, 'accesstoken')
    
    dprint(__name__, 1, "subtitle URL: {0}{1}", PMS_baseURL, path)
    dprint(__name__, 1, "xargs: {0}", xargs)
    
    request = urllib2.Request(PMS_baseURL+path , None, xargs)
    try:
        response = urllib2.urlopen(request, timeout=20)
    except urllib2.URLError as e:
        dprint(__name__, 0, 'No Response from Plex Media Server')
        if hasattr(e, 'reason'):
            dprint(__name__, 0, "We failed to reach a server. Reason: {0}", e.reason)
        elif hasattr(e, 'code'):
            dprint(__name__, 0, "The server couldn't fulfill the request. Error code: {0}", e.code)
        return False
    except IOError:
        dprint(__name__, 0, 'Error loading response XML from Plex Media Server')
        return False
    
    # Todo: Deal with ANSI files. How to select used "codepage"?
    subtitleFile = response.read()
    
    print response.headers
    
    dprint(__name__, 1, "====== received Subtitle ======")
    dprint(__name__, 1, "{0} [...]", subtitleFile[:255])
    dprint(__name__, 1, "====== Subtitle finished ======")
    
    if options['PlexConnectSubtitleFormat']=='srt':
        subtitle = parseSRT(subtitleFile)
    else:
        return False
    
    JSON = json.dumps(subtitle)
    
    dprint(__name__, 1, "====== generated subtitle aTV subtitle JSON ======")
    dprint(__name__, 1, "{0} [...]", JSON[:255])
    dprint(__name__, 1, "====== aTV subtitle JSON finished ======")
    return(JSON)



"""
parseSRT - decode SRT file, create aTV subtitle structure

parameters:
    SRT - big string containing the SRT file
result:
    JSON - subtitle encoded into .js tree to feed PlexConnect's updateSubtitle() (see application.js)
"""
def parseSRT(SRT):
    subtitle = { 'Timestamp': [] }
    
    srtPart = re.split(r'(\r\n|\n\r|\n|\r)\1+(?=[0-9]+)', SRT.strip())[::2];  # trim whitespaces, split at multi-newline, check for following number
    timeHide_last = 0
    
    for Item in srtPart:
        ItemPart = re.split(r'\r\n|\n\r|\n|\r', Item.strip());  # trim whitespaces, split at newline
        
        timePart = re.split(r':|,|-->', ItemPart[1]);  # <StartTime> --> <EndTime> split at : , or -->
        timeShow = int(timePart[0])*1000*60*60 +\
                   int(timePart[1])*1000*60 +\
                   int(timePart[2])*1000 +\
                   int(timePart[3]);
        timeHide = int(timePart[4])*1000*60*60 +\
                   int(timePart[5])*1000*60 +\
                   int(timePart[6])*1000 +\
                   int(timePart[7]);
        
        # switch off? skip if new msg at same point in time.
        if timeHide_last!=timeShow:
            subtitle['Timestamp'].append({ 'time': timeHide_last })
        timeHide_last = timeHide
        
        # current time
        subtitle['Timestamp'].append({ 'time': timeShow, 'Line': [] })
        #JSON += '  { "time":'+str(timeHide_last)+', "Line": [\n'
        
        # analyse format: <...> - i_talics (light), b_old (heavy), u_nderline (?), font color (?)
        frmt_i = False
        frmt_b = False
        for i, line in enumerate(ItemPart[2:]):  # evaluate each text line
            for frmt in re.finditer(r'<([^/]*?)>', line):  # format switch on in current line
                if frmt.group(1)=='i': frmt_i = True
                if frmt.group(1)=='b': frmt_b = True
            
            weight = ''  # determine aTV font - from previous line or current
            if frmt_i: weight = 'light'
            if frmt_b: weight = 'heavy'
            
            for frmt in re.finditer(r'</(.*?)>', line):  # format switch off
                if frmt.group(1)=='i': frmt_i = False
                if frmt.group(1)=='b': frmt_b = False
            
            line = re.sub('<.*?>', "", line);  # remove the formatting identifiers
            
            subtitle['Timestamp'][-1]['Line'].append({ 'text': line })
            if weight: subtitle['Timestamp'][-1]['Line'][-1]['weight'] = weight
    
    subtitle['Timestamp'].append({ 'time': timeHide_last })  # switch off last subtitle
    return subtitle



if __name__ == '__main__':
    SRT = "\
1\n\
00:00:0,123 --> 00:00:03,456\n\
<i>Hello World</i>\n\
\n\
2\n\
00:00:03,456 --> 00:00:06,000\n\
<b>Question -</b>\n\
Does it run?\n\
\n\
3\n\
00:00:08,000 --> 00:00:10,000\n\
Yes, Python works!\n\
\n\
"
    
    dprint('', 0, "SRT file")
    dprint('', 0, SRT[:1000])
    subtitle = parseSRT(SRT)
    JSON = json.dumps(subtitle)
    dprint('', 0, "aTV subtitle JSON")
    dprint('', 0, JSON[:1000])
    
"""
JSON result (about):
{ "Timestamp": [
  { "time":0 },
  { "time":123, "Line": [
    { "text":"Hello World", "weight": "light" }
    ]
  },
  { "time":3456, "Line": [
    { "text":"Question -", "weight": "heavy" },
    { "text":"Does it run?" }
    ]
  },
  { "time":6000 },
  { "time":8000, "Line": [
    { "text":"Yes, Python works!" }
    ]
  },
  { "time":10000 }
  ]
}
"""
