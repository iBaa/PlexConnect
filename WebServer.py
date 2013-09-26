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
from os import sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import ssl
from multiprocessing import Pipe  # inter process communication
import urllib
import signal

import Settings, ATVSettings
from Debug import *  # dprint()
import XMLConverter  # XML_PMS2aTV, XML_PlayVideo
import Localize



g_param = {}
def setParams(param):
    global g_param
    g_param = param



class MyHandler(BaseHTTPRequestHandler):
    
    # Fixes slow serving speed under Windows
    def address_string(self):
      host, port = self.client_address[:2]
      #return socket.getfqdn(host)
      return host
      
    def log_message(self, format, *args):
      pass
    
    def do_GET(self):
        try:
            dprint(__name__, 2, "http request header:\n{0}", self.headers)
            dprint(__name__, 2, "http request path:\n{0}", self.path)
            
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
            
            dprint(__name__, 2, "cleaned path:\n{0}", self.path)
            dprint(__name__, 2, "PlexConnect options:\n{0}", options)
            dprint(__name__, 2, "additional arguments:\n{0}", args)
            
            if 'User-Agent' in self.headers and \
               'AppleTV' in self.headers['User-Agent']:
                
                # recieve simple logging messages from the ATV
                if 'PlexConnectLog' in options:
                    dprint('ATVLogger', 0, options['PlexConnectLog'])
                    self.send_response(200)
                    self.send_header('Content-type', 'text/plain')
                    self.end_headers()
                    return
                
                # serve "application.js" to aTV
                # disregard the path - it is different for different iOS versions
                if self.path.endswith("application.js"):
                    dprint(__name__, 1, "serving application.js")
                    f = open(sys.path[0] + sep + "assets" + sep + "js" + sep + "application.js")
                    self.send_response(200)
                    self.send_header('Content-type', 'text/javascript')
                    self.end_headers()
                    self.wfile.write(f.read())
                    f.close()
                    return
                
                # serve all other .js files to aTV
                if self.path.endswith(".js"):
                    dprint(__name__, 1, "serving  " + sys.path[0] + sep + "assets" + self.path.replace('/',sep))
                    f = open(sys.path[0] + sep + "assets" + self.path.replace('/',sep))
                    self.send_response(200)
                    self.send_header('Content-type', 'text/javascript')
                    self.end_headers()
                    self.wfile.write(Localize.replaceTEXT(f.read(), options['aTVLanguage']).encode('utf-8'))
                    f.close()
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
                    XML = XMLConverter.XML_PMS2aTV(self.client_address, self.path + args, options)
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
    XMLConverter.discoverPMS()
    
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
    param['HostToIntercept'] = 'trailers.apple.com'
    param['HostOfPlexConnect'] = 'atv.plexconnect'
    
    if len(sys.argv)==1:
        Run(cmdPipe[1], param)
    elif len(sys.argv)==2 and sys.argv[1]=='SSL':
        Run_SSL(cmdPipe[1], param)
