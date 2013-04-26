#!/usr/bin/python

import time, uuid, hmac, hashlib, base64
from urllib import urlencode
from urlparse import urlparse

import Settings

Addr_PMS = Settings.getIP_PMS()+':'+str(Settings.getPort_PMS())

#Kindly borrowed from https://github.com/megawubs/pyplex/blob/master/plexAPI/info.py
def getTranscodeURL(path, ratingkey):
    args = dict()
    args['offset'] = 0
    args['3g'] = 0
    args['subtitleSize'] = 125
    args['secondsPerSegment'] = 10
    args['ratingKey'] = ratingkey
    args["identifier"] = 'com.plexapp.plugins.library'
    args["quality"] = 9
    args["url"] = "http://" + Addr_PMS + path
    args["httpCookies"] = ''
    args["userAgent"] = ''
    transcodeURL = '/video/:/transcode/segmented/start.m3u8?'
    transcodeURL += urlencode(args)
    atime = int(time.time())
    message = transcodeURL + "@%d" % atime
    publicKey = 'KQMIY6GATPC63AIMC4R2'
    privateKey = base64.b64decode('k3U6GLkZOoNIoSgjDshPErvqMIFdE0xMTx8kgsrhnC0=')
    sig = base64.b64encode(hmac.new(privateKey, msg=message, digestmod=hashlib.sha256).digest())
    plexAccess = dict()
    plexAccess['X-Plex-Access-Key'] = publicKey
    plexAccess['X-Plex-Access-Time'] = atime
    plexAccess['X-Plex-Access-Code'] = sig
    plexAccess['X-Plex-Client-Capabilities'] = 'protocols=http-live-streaming,http-mp4-streaming,http-mp4-video,http-mp4-video-720p,http-streaming-video,http-streaming-video-720p;videoDecoders=h264{profile:high&resolution:720&level:41};audioDecoders=aac,mp3,ac3'
    transcodeURL = transcodeURL + "&" + urlencode(plexAccess)
    return "%s%s%s" % ("http://", Addr_PMS, transcodeURL)
