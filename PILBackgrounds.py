#!/usr/bin/env python

import re
import sys
import io
import urllib
import urllib2
import urlparse
import posixpath
import traceback

import os.path
from Debug import * 

try:
    from PIL import Image, ImageFilter
    __isPILinstalled = True
except ImportError:
    __isPILinstalled = False



def generate(PMS_uuid, url, authtoken, resolution, blurRadius):
    cachepath = sys.path[0]+"/assets/fanartcache"
    stylepath = sys.path[0]+"/assets/thumbnails"

    # Create cache filename
    id = re.search('/library/metadata/(?P<ratingKey>\S+)/art/(?P<fileId>\S+)', url)
    if id:
        # assumes URL in format "/library/metadata/<ratingKey>/art/fileId>"
        id = id.groupdict()
        cachefile = urllib.quote_plus(PMS_uuid +"_"+ id['ratingKey'] +"_"+ id['fileId'] +"_"+ resolution +"_"+ blurRadius) + ".jpg"
    else:
        fileid = posixpath.basename(urlparse.urlparse(url).path)
        cachefile = urllib.quote_plus(PMS_uuid +"_"+ fileid +"_"+ resolution +"_"+ blurRadius) + ".jpg"  # quote: just to make sure...
    
    # Already created?
    dprint(__name__, 1, 'Check for Cachefile.')  # Debug
    if os.path.isfile(cachepath+"/"+cachefile):
        dprint(__name__, 1, 'Cachefile  found.')  # Debug
        return "/fanartcache/"+cachefile
    
    # No! Request Background from PMS
    dprint(__name__, 1, 'No Cachefile found. Generating Background.')  # Debug
    try:
        dprint(__name__, 1, 'Getting Remote Image.')  # Debug
        xargs = {}
        if authtoken:
            xargs['X-Plex-Token'] = authtoken
        request = urllib2.Request(url, None, xargs)
        response = urllib2.urlopen(request).read()
        background = Image.open(io.BytesIO(response))
    except urllib2.URLError as e:
        dprint(__name__, 0, 'URLError: {0} // url: {1}', e.reason, url)
        return "/thumbnails/Background_blank_" + resolution + ".jpg"
    except urllib2.HTTPError as e:
        dprint(__name__, 0, 'HTTPError: {0} {1} // url: {2}', str(e.code), e.msg, url)
        return "/thumbnails/Background_blank_" + resolution + ".jpg"
    except IOError as e:
        dprint(__name__, 0, 'IOError: {0} // url: {1}', str(e), url)
        return "/thumbnails/Background_blank_" + resolution + ".jpg"
    
    blurRadius = int(blurRadius)
    
    # Get gradient template
    dprint(__name__, 1, 'Merging Layers.')  # Debug
    if resolution == '1080':
        width = 1920
        height = 1080
        blurRegion = (0, 514, 1920, 1080)
        layer = Image.open(stylepath + "/gradient_1080.png")
    else:
        width = 1280
        height = 720
        blurRegion = (0, 342, 1280, 720)
        blurRadius = int(blurRadius / 1.5)
        layer = Image.open(stylepath + "/gradient_720.png")
    
    try:
        # Set background resolution and merge layers
        bgWidth, bgHeight = background.size
        dprint(__name__,1 ,"Background size: {0}, {1}", bgWidth, bgHeight)
        dprint(__name__,1 , "aTV Height: {0}, {1}", width, height)
        
        if bgHeight != height:
            background = background.resize((width, height), Image.ANTIALIAS)
            dprint(__name__,1 , "Resizing background")
        
        if blurRadius != 0:
            dprint(__name__,1 , "Blurring Lower Region")
            imgBlur = background.crop(blurRegion)
            imgBlur = imgBlur.filter(ImageFilter.GaussianBlur(blurRadius))
            background.paste(imgBlur, blurRegion)
            
        background.paste(layer, ( 0, 0), layer)
        
        # Save to Cache
        background.save(cachepath+"/"+cachefile)
    except:
        dprint(__name__, 0, 'Error - Failed to generate background image.\n{0}', traceback.format_exc())
        return "/thumbnails/Background_blank_" + resolution + ".jpg"
    
    dprint(__name__, 1, 'Cachefile  generated.')  # Debug
    return "/fanartcache/"+cachefile



# HELPERS

def isPILinstalled():
    return __isPILinstalled



if __name__=="__main__":
    url = "http://thetvdb.com/banners/fanart/original/95451-23.jpg"
    res = generate('uuid', url, 'authtoken', '1080')
    res = generate('uuid', url, 'authtoken', '720')
    dprint(__name__, 0, "Background: {0}", res)
