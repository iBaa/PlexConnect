#!/usr/bin/python

"""
Sources:
http://fragments.turtlemeat.com/pythonwebserver.php
http://www.linuxjournal.com/content/tech-tip-really-simple-http-server-python
...stackoverflow.com and such
"""


import sys
import string, cgi, time
from os import sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import Queue  # inter process communication

try:
    import xml.etree.cElementTree as etree
except ImportError:
    import xml.etree.ElementTree as etree

import ATVSettings
from Debug import *  # dprint()
import XMLConverter  # XML_PMS2aTV, XML_PlayVideo



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

    def do_GET(self):
        try:
            dprint(__name__, 2, "http request header:\n{0}", self.headers)
            dprint(__name__, 2, "http request path:\n{0}", self.path)

            # brake up path, separate PlexConnect options
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
                    options[parts[0]] = parts[1]

            dprint(__name__, 2, "cleaned path:\n{0}", self.path)
            dprint(__name__, 2, "request options:\n{0}", options)

            if 'Host' in self.headers and \
               'User-Agent' in self.headers and \
               self.headers['Host'] == g_param['HostToIntercept'] and \
               'AppleTV' in self.headers['User-Agent']:

                # recieve simple logging messages from the ATV
                if self.path.endswith("&atvlogger"):
                    msg = self.path.replace("%20", " ")
                    msg = msg.replace("&lt;", "<")
                    msg = msg.replace("&gt;", ">")
                    msg = msg.replace("&fs;", "/")
                    msg = msg.replace("&qo;", '"')
                    msg = msg[1:len(msg)-10]
                    dprint('ATVLogger', 0, msg)
                    self.send_response(200)
                    self.send_header('Content-type', 'text/plain')
                    self.end_headers()
                    return

                # serve "application.js" to aTV
                # disregard the path - it is different for different iOS versions
                if self.path.endswith("application.js"):
                    dprint(__name__, 1, "serving application.js")
                    f = open(sys.path[0] + sep + "assets" + sep + "application.js")
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(f.read())
                    f.close()
                    return

                # serve all other .js files to aTV
                if self.path.endswith(".js"):
                    dprint(__name__, 1, "serving  " + sys.path[0] + sep + "assets" + self.path.replace('/',sep))
                    f = open(sys.path[0] + sep + "assets" + self.path.replace('/',sep))
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(f.read())
                    f.close()
                    return

                # serve all .xml files to aTV including "plexconnect.xml" or "plexconnect_oldmenu.xml"
                if self.path.endswith(".xml"):
                    dprint(__name__,1,"serving "+ sys.path[0] + sep + "assets" + self.path.replace('/',sep))
                    f = open(sys.path[0] + sep + "assets" + self.path.replace('/',sep))
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(f.read())
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
                    XML = XMLConverter.XML_PMS2aTV(self.client_address, self.path, options)
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
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



def Run(cmdQueue, param):
    dinit(__name__, param)  # init logging, WebServer process

    #Protocol     = "HTTP/1.0"
    # todo: IP, port
    try:
        server = HTTPServer(('',81), MyHandler)
        server.timeout = 1
        sa = server.socket.getsockname()
    except Exception, e:
        dprint(__name__, 0, "Failed to connect to port 80 (http): {0}", e)
        sys.exit(1)

    dprint(__name__, 0, "***")
    dprint(__name__, 0, "WebServer: Serving HTTP on {0} port {1}.", sa[0], sa[1])
    dprint(__name__, 0, "***")

    setParams(param)
    XMLConverter.setParams(param)
    cfg = ATVSettings.CATVSettings()
    XMLConverter.setATVSettings(cfg)

    try:
        while True:
            # check command
            try:
                # check command
                cmd = cmdQueue.get_nowait()
                if cmd=='shutdown':
                    break

            except Queue.Empty:
                pass

            # do your work (with timeout)
            server.handle_request()

    except KeyboardInterrupt:
        dprint(__name__, 0,"^C received.")
    finally:
        dprint(__name__, 0, "Shutting down.")
        cfg.saveSettings()
        del cfg
        server.socket.close()



if __name__=="__main__":
    cmd = Queue.Queue()
    Run(cmd)