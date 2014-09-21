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
from SocketServer import ThreadingMixIn
import ssl
from multiprocessing import Pipe  # inter process communication
import urllib

import Settings, ATVSettings
from Debug import *  # dprint()
import XMLConverter  # XML_PMS2aTV, XML_PlayVideo
import re
import Localize
import Subtitle



g_param = {}
def setParams(param):
    global g_param
    g_param = param



def JSConverter(file, options):
    f = open(sys.path[0] + "/assets/js/" + file)
    JS = f.read()
    f.close()
    
    # PlexConnect {{URL()}}->baseURL
    for path in set(re.findall(r'\{\{URL\((.*?)\)\}\}', JS)):
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
            # clean path needed for filetype decoding
            parts = re.split(r'[?&]', self.path, 1)  # should be '?' only, but we do some things different :-)
            if len(parts)==1:
                self.path = parts[0]
                options = {}
                query = ''
            else:
                self.path = parts[0]
                
                # break up query string
                options = {}
                query = ''
                parts = parts[1].split('&')
                for part in parts:
                    if part.startswith('PlexConnect'):
                        # get options[]
                        opt = part.split('=', 1)
                        if len(opt)==1:
                            options[opt[0]] = ''
                        else:
                            options[opt[0]] = urllib.unquote(opt[1])
                    else:
                        # recreate query string (non-PlexConnect) - has to be merged back when forwarded
                        if query=='':
                            query = '?' + part
                        else:
                            query += '&' + part
            
            # get aTV language setting
            options['aTVLanguage'] = Localize.pickLanguage(self.headers.get('Accept-Language', 'en'))
            
            # add client address - to be used in case UDID is unknown
            if 'X-Forwarded-For' in self.headers:
                options['aTVAddress'] = self.headers['X-Forwarded-For'].split(',', 1)[0]
            else:
                options['aTVAddress'] = self.client_address[0]
            
            # get aTV hard-/software parameters
            options['aTVFirmwareVersion'] = self.headers.get('X-Apple-TV-Version', '5.1')
            options['aTVScreenResolution'] = self.headers.get('X-Apple-TV-Resolution', '720')
            
            dprint(__name__, 2, "pms address:\n{0}", PMSaddress)
            dprint(__name__, 2, "cleaned path:\n{0}", self.path)
            dprint(__name__, 2, "PlexConnect options:\n{0}", options)
            dprint(__name__, 2, "additional arguments:\n{0}", query)
            
            if 'User-Agent' in self.headers and \
               'AppleTV' in self.headers['User-Agent']:
                
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
                if basename in ("application.js", "main.js", "javascript-packed.js", "bootstrap.js") or \
                   basename.endswith(".js") and dirname == '/js':
                    if basename in ("main.js", "javascript-packed.js", "bootstrap.js"):
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
                
                # serve subtitle file - transcoded to aTV subtitle json
                if 'PlexConnect' in options and \
                   options['PlexConnect']=='Subtitle':
                    dprint(__name__, 1, "serving subtitle: "+self.path)
                    XML = Subtitle.getSubtitleJSON(PMSaddress, self.path + query, options)
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(XML)
                    return
                
                # get everything else from XMLConverter - formerly limited to trailing "/" and &PlexConnect Cmds
                if True:
                    dprint(__name__, 1, "serving .xml: "+self.path)
                    XML = XMLConverter.XML_PMS2aTV(PMSaddress, self.path + query, options)
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



class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""



def Run(cmdPipe, param):
    dinit(__name__, param)  # init logging, WebServer process
    
    cfg_IP_WebServer = param['IP_self']
    cfg_Port_WebServer = param['CSettings'].getSetting('port_webserver')
    try:
        server = ThreadedHTTPServer((cfg_IP_WebServer,int(cfg_Port_WebServer)), MyHandler)
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
        dprint(__name__, 0,"^C received.")
    finally:
        dprint(__name__, 0, "Shutting down.")
        cfg.saveSettings()
        del cfg
        server.socket.close()



def Run_SSL(cmdPipe, param):
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
        server = ThreadedHTTPServer((cfg_IP_WebServer,int(cfg_Port_SSL)), MyHandler)
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
