#!/usr/bin/env python

import re
import sys
import io
import urllib
import urllib2

import ConfigParser

import os.path
import unicodedata
from Debug import * 

try:
    from PIL import Image
    __isPILinstalled = True
except ImportError:
    dprint(__name__, 0, "No PIL/Pillow installation found.")
    __isPILinstalled = False



def generate(title, url, resolution):
    cachepath = sys.path[0]+"/assets/fanartcache"
    stylepath = sys.path[0]+"/assets/templates/images"
    cachefile = normalizeString(title) + "_" + normalizeString(resolution) + ".jpg"
    
    # Already created?
    dprint(__name__, 1, 'Check for Cachefile.')  # Debug
    if os.path.isfile(cachepath+"/"+cachefile):
        dprint(__name__, 1, 'Cachefile  found.')  # Debug
        return "/fanartcache/"+cachefile
    
    # No! Request Background from PMS
    dprint(__name__, 1, 'No Cachefile found. Generating Background.')  # Debug
    try:
        dprint(__name__, 1, 'Getting Remote Image.')  # Debug
        response = urllib2.urlopen(url)
        background = Image.open(io.BytesIO(response.read()))
    except urllib2.URLError, e:
        dprint(__name__, 1, 'error: {0} {1} // url: {2}', str(e.code), e.msg, url)  # Debug
        background = Image.open(stylepath+"/blank.jpg")
    
    # Get gradient template
    dprint(__name__, 1, 'Merging Layers.')  # Debug
    if resolution == '1080':
        width = 1920
        height = 1080
        layer = Image.open(stylepath + "/gradient_1080.png")
    else:
        width = 1280
        height = 720
        layer = Image.open(stylepath + "/gradient_720.png")
    
    # Set background resolution and merge layers
    bgWidth, bgHeight = background.size
    dprint(__name__,1 ,"Background size: {0}, {1}", bgWidth, bgHeight)
    dprint(__name__,1 , "aTV Height: {0}, {1}", width, height)
    
    if bgHeight != height:
        background = background.resize((width, height), Image.ANTIALIAS)
        dprint(__name__,1 , "Resizing background")   
    
    background.paste(layer, ( 0, 0), layer)
    
    # Save to Cache
    background.save(cachepath+"/"+cachefile)  
    dprint(__name__, 1, 'Cachefile  generated.')  # Debug
    return "/fanartcache/"+cachefile



# HELPERS

def isPILinstalled():
    return __isPILinstalled

def normalizeString(text):
    text = urllib.unquote(str(text)).replace(' ','+')
    text = unicodedata.normalize('NFKD',unicode(text,"utf8")).encode("ascii","ignore")  # Only ASCII CHARS
    text = re.sub(r'\W+', '+', text) # No Special Chars  
    return text



if __name__=="__main__":
    url = "http://192.168.178.22:32400/photo/:/transcode/1920x1080/http%3A%2F%2F127.0.0.1%3A32400%2Flibrary%2Fmetadata%2F24466%2Fart%2F1412512746?url=http%3A%2F%2F127.0.0.1%3A32400%2Flibrary%2Fmetadata%2F24466%2Fart%2F1412512746&width=1920&height=1080"
    res = generate('TestBackground', url, '1080')
    dprint(__name__, 0, "Background: {0}", res)
