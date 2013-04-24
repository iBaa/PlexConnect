#!/usr/bin/python

"""
Sources:
http://fragments.turtlemeat.com/pythonwebserver.php
http://www.linuxjournal.com/content/tech-tip-really-simple-http-server-python
...stackoverflow.com and such
"""


import sys
import string, cgi, time
from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import Queue  # inter process communication

try:
    import xml.etree.cElementTree as etree
except ImportError:
    import xml.etree.ElementTree as etree

import Settings
from Debug import *  # dprint()
import XMLConverter  # XML_PMS2aTV, XML_PlayVideo



class MyHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        try:
            if self.client_address[0]==Settings.getIP_aTV():
                
                # serve "application.js" to aTV
                # disregard the path - it is different for different iOS versions
                if self.path.endswith("application.js"):
                    dprint(__name__, 1, "serving application.js")
                    f = open(curdir + sep + "assets" + sep + "application.js")
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(f.read())
                    f.close()
                    return
                
                # serve "plexconnect.xml" or "plexconnect_oldmenu.xml" to aTV
                if self.path.endswith("plexconnect.xml") or self.path.endswith("plexconnect_oldmenu.xml"):
                    dprint(__name__,1,"serving "+ curdir + sep + "assets" + self.path.replace('/',sep));
                    f = open(curdir + sep + "assets" + self.path.replace('/',sep))
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(f.read())
                    f.close()
                    return
                
                # serve "*.jpg" - thumbnails for old-style mainpage
                if self.path.endswith(".jpg"):
                    dprint(__name__, 1, "serving *.jpg: "+self.path)
                    f = open(curdir + sep + "assets" + self.path, "rb")
                    self.send_response(200)
                    self.send_header('Content-type', 'image/jpeg')
                    self.end_headers()
                    self.wfile.write(f.read())
                    f.close()
                    return
                
                # serve Plex directory structure - make sure to keep the trailing "/"                
                if self.path.endswith("/"):
                    dprint(__name__, 1, "serving .xml: "+self.path)
                    XML = XMLConverter.XML_PMS2aTV(self.client_address, self.path)
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(XML)
                    return
                
                # serve Plex media
                if self.path.endswith("&PlexConnect=Play"):
                    dprint(__name__, 1, "serving media: "+self.path)
                    XML = XMLConverter.XML_PlayVideo(self.client_address, self.path[:-len('&PlexConnect=Play')])
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(XML)
                    return
                
                # unexpected request
                self.send_error(403,"Access denied: %s" % self.path)
            
            else:
                self.send_error(403,"Not Serving Client %s" % self.client_address[0])
        except IOError:
            self.send_error(404,"File Not Found: %s" % self.path)



def Run(cmdQueue):
    #Protocol     = "HTTP/1.0"
    # todo: IP, port
    try:
        server = HTTPServer(('',80), MyHandler)
        server.timeout = 1
        sa = server.socket.getsockname()
        
        dprint(__name__, 0, "***")
        dprint(__name__, 0, "WebServer: Serving HTTP on {} port {}.", sa[0], sa[1])
        dprint(__name__, 0, "***")
        
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
        server.socket.close()



if __name__=="__main__":
    cmd = Queue.Queue()
    Run(cmd)