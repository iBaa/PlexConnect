#!/usr/bin/env python

"""
Sources:
http://fragments.turtlemeat.com/pythonwebserver.php
http://www.linuxjournal.com/content/tech-tip-really-simple-http-server-python
...stackoverflow.com and such

after 27Aug - Apple's switch to https:
- added https WebServer with SSL encryption - needs valid (private) vertificate on aTV and server
- for additional information see http://langui.sh/2013/08/27/appletv-ssl-plexconnect/
Thanks to reaperhulk for showing this solution!
"""


import sys
import string, cgi, time
from os import sep, path
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import ssl
from multiprocessing import Pipe  # inter process communication
import urllib
import signal

import Settings, ATVSettings
from Debug import *  # dprint()
import XMLConverter  # XML_PMS2aTV, XML_PlayVideo
import re
import Localize



g_param = {}
def setParams(param):
    global g_param
    g_param = param



def JSConverter(file, options):
    f = open(sys.path[0] + "/assets/js/" + file)
    JS = f.read()
    f.close()
    
    # PlexConnect {{URL()}}->baseURL
    for path in set(re.findall(r'\{\{URL\((.+?)\)\}\}', JS)):
        JS = JS.replace('{{URL(%s)}}' % path, g_param['baseURL']+path)
    
    # localization
    JS = Localize.replaceTEXT(JS, options['aTVLanguage']).encode('utf-8')
    
    return JS



class MyHandler(BaseHTTPRequestHandler):
    
    # Fixes slow serving speed under Windows
    def address_string(self):
      host, port = self.client_address[:2]
      #return socket.getfqdn(host)
      return host
      
    def log_message(self, format, *args):
      pass
    
    def do_GET(self):
        global g_param
        try:
            dprint(__name__, 2, "http request header:\n{0}", self.headers)
            dprint(__name__, 2, "http request path:\n{0}", self.path)
            
            # check for PMS address
            PMSaddress = ''
            pms_end = self.path.find(')')
            if self.path.startswith('/PMS(') and pms_end>-1:
                PMSaddress = urllib.unquote_plus(self.path[5:pms_end])
                self.path = self.path[pms_end+1:]
            
            # break up path, separate PlexConnect options
            options = {}
            while True:
                cmd_start = self.path.find('&PlexConnect')
                cmd_end = self.path.find('&', cmd_start+1)
                
                if cmd_start==-1:
                    break
                if cmd_end>-1:
                    cmd = self.path[cmd_start+1:cmd_end]
                    self.path = self.path[:cmd_start] + self.path[cmd_end:]
                else:
                    cmd = self.path[cmd_start+1:]
                    self.path = self.path[:cmd_start]
                
                parts = cmd.split('=', 1)
                if len(parts)==1:
                    options[parts[0]] = ''
                else:
                    options[parts[0]] = urllib.unquote(parts[1])
            
            # break up path, separate additional arguments
            # clean path needed for filetype decoding... has to be merged back when forwarded.
            parts = self.path.split('?', 1)
            if len(parts)==1:
                args = ''
            else:
                self.path = parts[0]
                args = '?'+parts[1]
            
            # get aTV language setting
            options['aTVLanguage'] = Localize.pickLanguage(self.headers.get('Accept-Language', 'en'))
            
            # add client address - to be used in case UDID is unknown
            options['aTVAddress'] = self.client_address[0]
            
            # get aTV hard-/software parameters
            options['aTVFirmwareVersion'] = self.headers.get('X-Apple-TV-Version', '5.1')
            options['aTVScreenResolution'] = self.headers.get('X-Apple-TV-Resolution', '720')
            
            dprint(__name__, 2, "pms address:\n{0}", PMSaddress)
            dprint(__name__, 2, "cleaned path:\n{0}", self.path)
            dprint(__name__, 2, "PlexConnect options:\n{0}", options)
            dprint(__name__, 2, "additional arguments:\n{0}", args)
                    
            if 'User-Agent' in self.headers and \
               'AppleTV' in self.headers['User-Agent']:
                
                # serve the plex icon
                if self.headers['Host'] == 'a1.phobos.apple.com' and self.path.endswith(".png"):
                    # possible icon
                    basename = path.basename(self.path)
                    iconname, ext = basename.split('.')
                    dprint(__name__, 2, "serving icon {0}", iconname)
                    name, rez = iconname.split('@')
                    dprint(__name__, 2, "icon name: {0} at {1}", name, rez)
                    hosticons = {
                        'www.icloud.com': 'iMovieNewAuth',
                        'atv.hbogo.com': 'vega',
                        'atv.qello.com': 'qello',
                        'a248.e.akamai.net': 'hulu',
                        'appletv.vevo.com': 'com.vevo.appletv',
                        'apps.sho.com': 'com.smithsonian.appletv',
                        'appletv.watchdisneyjunior.go.com': 'com.disney.junior.appletv',
                        'appletv.watchdisneychannel.go.com': 'com.disney.channel.appletv',
                        'appletv.watchdisneyxd.go.com': 'com.disney.xd.appletv',
                        'ssl.weather.com': 'com.weather.appletv',
                        'secure.marketwatch.com': 'wsj',
                        'trailers.apple.com': 'movie-trailers',
                        'secure.showtimeanytime.com': 'com.showtime.appletv',
                        'vimeo.com': 'vimeo',
                        'd6mhwe3a8uvr5.cloudfront.net': 'skynews',
                        'video.pbs.org': 'com.pbs.appletv',
                        'neulion-a.akamaihd.net': 'com.mlssoccer.appletv',
                        'itunesconnect.apple.com': 'iTunesConnect',
                        'abcnews.go.com': 'com.abcnews.appletv',
                        'atvapp.willow.tv': 'com.willowtv.appletv',
                        'player.aetndigital.com': 'com.aenetworks.lifetime.appletv',
                        'www.crunchyroll.com': 'crunchyroll',
                        'watchabc.go.com': 'com.abc.appletv.v2',
                        'appletv.redbull.tv': 'com.redbulltv.appletv',
                        'neulion-a.akamaihd.net': 'NHL',
                        'appletv.cnbc.com': 'com.cnbc.appletv',
                        'appletv.now.nfl.com': 'com.nfl.now.appletv',
                        'secure.net.wwe.com': 'com.wwe.appletv.v2',
                        'api-global.netflix.com': 'netflix',
                        'player.aetndigital.com': 'com.aenetworks.appletv',
                        's.yimg.com': 'com.yahoo.screen.appletv',
                        'kids.pbs.org': 'com.pbskids.appletv.v2',
                        'kortv.com': 'com.wkntv.appletv',
                        'appletv.crackle.com': 'com.crackle.appletv.v2',
                        'd1d0j1u9ayd8uc.cloudfront.net': 'com.acc.appletv',
                        's.cdn.turner.com': 'nba',
                        'player.aetndigital.com': 'com.aenetworks.history.appletv',
                        'aptve.foxneodigital.com': 'com.foxnow.appletv',
                        'appletv.flickr.com': 'flickr',
                        'a248.e.akamai.net': 'carterville',
                        'securea.mlb.com': 'flagstaff',
                        'mobapi.bloomberg.com': 'com.bloomberg.appletv',
                        'aptve-fx.foxneodigital.com': 'com.fxnow.appletv',
                        'festival.itunes.apple.com': 'com.festival.appletv',
                        's.aolcdn.com': 'com.aolon.appletv'
                    }
                    if name == hosticons.get(g_param['HostToIntercept']):
                        dprint(__name__, 2, "getting plex icon")
                        f = open(sys.path[0] + sep + "assets" + sep + "thumbnails" + sep + "icon@" + rez + ".png", "rb")
                        self.send_response(200)
                        self.send_header('Content-type', 'image/png')
                        self.end_headers()
                        self.wfile.write(f.read())
                        f.close()
                        return
                    else:
                        dprint(__name__, 2, "getting app icon")
                        self.send_response(200)
                        self.send_header('Content-type', 'image/png')
                        self.end_headers()
                        self.wfile.write(urllib.urlopen('http://' + self.headers['Host'] + self.path).read())
                        return
                elif self.headers['Host'] == 'a1.phobos.apple.com':
                	# something other than an icon was requested
                    self.send_response(200)
                    self.send_header('Content-type', self.headers['Content-type'])
                    self.end_headers()
                    self.wfile.write(urllib.urlopen('http://' + self.headers['Host'] + self.path).read())
                    return
                
                # recieve simple logging messages from the ATV
                if 'PlexConnectATVLogLevel' in options:
                    dprint('ATVLogger', int(options['PlexConnectATVLogLevel']), options['PlexConnectLog'])
                    self.send_response(200)
                    self.send_header('Content-type', 'text/plain')
                    self.end_headers()
                    return
                    
                # serve "*.cer" - Serve up certificate file to atv
                if self.path.endswith(".cer"):
                    dprint(__name__, 1, "serving *.cer: "+self.path)
                    if g_param['CSettings'].getSetting('certfile').startswith('.'):
                        # relative to current path
                        cfg_certfile = sys.path[0] + sep + g_param['CSettings'].getSetting('certfile')
                    else:
                        # absolute path
                        cfg_certfile = g_param['CSettings'].getSetting('certfile')
                    cfg_certfile = path.normpath(cfg_certfile)
                    
                    cfg_certfile = path.splitext(cfg_certfile)[0] + '.cer'
                    try:
                        f = open(cfg_certfile, "rb")
                    except:
                        dprint(__name__, 0, "Failed to access certificate: {0}", cfg_certfile)
                        return
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'text/xml')
                    self.end_headers()
                    self.wfile.write(f.read())
                    f.close()
                    return 
                
                # serve .js files to aTV
                # application, main: ignore path, send /assets/js/application.js
                # otherwise: path should be '/js', send /assets/js/*.js
                dirname = path.dirname(self.path)
                basename = path.basename(self.path)
                if basename in ("application.js", "main.js", "javascript-packed.js") or \
                   basename.endswith(".js") and dirname == '/js':
                    if basename in ("main.js", "javascript-packed.js"):
                        basename = "application.js"
                    dprint(__name__, 1, "serving /js/{0}", basename)
                    JS = JSConverter(basename, options)
                    self.send_response(200)
                    self.send_header('Content-type', 'text/javascript')
                    self.end_headers()
                    self.wfile.write(JS)
                    return
                
                # serve "*.jpg" - thumbnails for old-style mainpage
                if self.path.endswith(".jpg"):
                    dprint(__name__, 1, "serving *.jpg: "+self.path)
                    f = open(sys.path[0] + sep + "assets" + self.path, "rb")
                    self.send_response(200)
                    self.send_header('Content-type', 'image/jpeg')
                    self.end_headers()
                    self.wfile.write(f.read())
                    f.close()
                    return
                
                # serve "*.png" - only png's support transparent colors
                if self.path.endswith(".png"):
                    dprint(__name__, 1, "serving *.png: "+self.path)
                    f = open(sys.path[0] + sep + "assets" + self.path, "rb")
                    self.send_response(200)
                    self.send_header('Content-type', 'image/png')
                    self.end_headers()
                    self.wfile.write(f.read())
                    f.close()
                    return
                
                # get everything else from XMLConverter - formerly limited to trailing "/" and &PlexConnect Cmds
                if True:
                    dprint(__name__, 1, "serving .xml: "+self.path)
                    XML = XMLConverter.XML_PMS2aTV(PMSaddress, self.path + args, options)
                    self.send_response(200)
                    self.send_header('Content-type', 'text/xml')
                    self.end_headers()
                    self.wfile.write(XML)
                    return
                
                """
                # unexpected request
                self.send_error(403,"Access denied: %s" % self.path)
                """
            
            else:
                self.send_error(403,"Not Serving Client %s" % self.client_address[0])
        except IOError:
            self.send_error(404,"File Not Found: %s" % self.path)



def Run(cmdPipe, param):
    if not __name__ == '__main__':
        signal.signal(signal.SIGINT, signal.SIG_IGN)
    
    dinit(__name__, param)  # init logging, WebServer process
    
    cfg_IP_WebServer = param['IP_self']
    cfg_Port_WebServer = param['CSettings'].getSetting('port_webserver')
    try:
        server = HTTPServer((cfg_IP_WebServer,int(cfg_Port_WebServer)), MyHandler)
        server.timeout = 1
    except Exception, e:
        dprint(__name__, 0, "Failed to connect to HTTP on {0} port {1}: {2}", cfg_IP_WebServer, cfg_Port_WebServer, e)
        sys.exit(1)
    
    socketinfo = server.socket.getsockname()
    
    dprint(__name__, 0, "***")
    dprint(__name__, 0, "WebServer: Serving HTTP on {0} port {1}.", socketinfo[0], socketinfo[1])
    dprint(__name__, 0, "***")
    
    setParams(param)
    XMLConverter.setParams(param)
    cfg = ATVSettings.CATVSettings()
    XMLConverter.setATVSettings(cfg)
    
    try:
        while True:
            # check command
            if cmdPipe.poll():
                cmd = cmdPipe.recv()
                if cmd=='shutdown':
                    break
            
            # do your work (with timeout)
            server.handle_request()
    
    except KeyboardInterrupt:
        signal.signal(signal.SIGINT, signal.SIG_IGN)  # we heard you!
        dprint(__name__, 0,"^C received.")
    finally:
        dprint(__name__, 0, "Shutting down.")
        cfg.saveSettings()
        del cfg
        server.socket.close()



def Run_SSL(cmdPipe, param):
    if not __name__ == '__main__':
        signal.signal(signal.SIGINT, signal.SIG_IGN)
    
    dinit(__name__, param)  # init logging, WebServer process
    
    cfg_IP_WebServer = param['IP_self']
    cfg_Port_SSL = param['CSettings'].getSetting('port_ssl')
    
    if param['CSettings'].getSetting('certfile').startswith('.'):
        # relative to current path
        cfg_certfile = sys.path[0] + sep + param['CSettings'].getSetting('certfile')
    else:
        # absolute path
        cfg_certfile = param['CSettings'].getSetting('certfile')
    cfg_certfile = path.normpath(cfg_certfile)
    
    try:
        certfile = open(cfg_certfile, 'r')
    except:
        dprint(__name__, 0, "Failed to access certificate: {0}", cfg_certfile)
        sys.exit(1)
    certfile.close()
    
    try:
        server = HTTPServer((cfg_IP_WebServer,int(cfg_Port_SSL)), MyHandler)
        server.socket = ssl.wrap_socket(server.socket, certfile=cfg_certfile, server_side=True)
        server.timeout = 1
    except Exception, e:
        dprint(__name__, 0, "Failed to connect to HTTPS on {0} port {1}: {2}", cfg_IP_WebServer, cfg_Port_SSL, e)
        sys.exit(1)
    
    socketinfo = server.socket.getsockname()
    
    dprint(__name__, 0, "***")
    dprint(__name__, 0, "WebServer: Serving HTTPS on {0} port {1}.", socketinfo[0], socketinfo[1])
    dprint(__name__, 0, "***")
    
    setParams(param)
    
    try:
        while True:
            # check command
            if cmdPipe.poll():
                cmd = cmdPipe.recv()
                if cmd=='shutdown':
                    break
            
            # do your work (with timeout)
            server.handle_request()
    
    except KeyboardInterrupt:
        signal.signal(signal.SIGINT, signal.SIG_IGN)  # we heard you!
        dprint(__name__, 0,"^C received.")
    finally:
        dprint(__name__, 0, "Shutting down.")
        server.socket.close()



if __name__=="__main__":
    cmdPipe = Pipe()
    
    cfg = Settings.CSettings()
    param = {}
    param['CSettings'] = cfg
    
    param['IP_self'] = '192.168.178.20'  # IP_self?
    param['baseURL'] = 'http://'+ param['IP_self'] +':'+ cfg.getSetting('port_webserver')
    param['HostToIntercept'] = 'trailers.apple.com'
    
    if len(sys.argv)==1:
        Run(cmdPipe[1], param)
    elif len(sys.argv)==2 and sys.argv[1]=='SSL':
        Run_SSL(cmdPipe[1], param)
