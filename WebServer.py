#!/usr/bin/python

"""
Sources:
http://fragments.turtlemeat.com/pythonwebserver.php
http://www.linuxjournal.com/content/tech-tip-really-simple-http-server-python
...stackoverflow.com and such
"""


import sys
#import inspect 
import string, cgi, time
from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
#import httplib, socket

try:
    import xml.etree.cElementTree as etree
except ImportError:
    import xml.etree.ElementTree as etree

import Settings
import XMLConverter  # XML_PMS2aTV, XML_PlayVideo



class MyHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        try:
            if self.client_address[0]==Settings.getIP_aTV():
                # serve "application.js" to aTV
                # disregard the path - it is different for different iOS versions
                if self.path.endswith("application.js"):
                    print "serving application.js"
                    f = open(curdir + sep + "assets" + sep + "application.js")
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(f.read())
                    f.close()
                    return
                
                # serve "plexconnect.xml" to aTV
                if self.path.endswith("plexconnect.xml"):
                    print "serving plexconnet.xml"
                    f = open(curdir + sep + "assets" + sep + "plexconnect.xml")
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(f.read())
                    f.close()
                    return
                
                # serve Plex directory structure - make sure to keep the trailing "/"                
                if self.path.endswith("/"):
                    print "serving .xml: "+self.path
                    XML = XMLConverter.XML_PMS2aTV(self.client_address, self.path)
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(XML)
                    return
                
                # serve Plex media
                print self.headers
                if self.path.endswith("&PlexConnect=Play"):
                    print "serving media: "+self.path
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



KeepRunning = True
def SetKeepRunning(in_KeepRunning):
    KeepRunning = in_KeepRunning



def Run():
    #Protocol     = "HTTP/1.0"
    # todo: IP, port
    global KeepRunning
    try:
        server = HTTPServer(('',80), MyHandler)
        
        sa = server.socket.getsockname()
        print "***"
        print "WebServer: Serving HTTP on", sa[0], "port", sa[1], "..."
        print "***"
        while KeepRunning:
            server.handle_request()
            
        print "WebServer: Shutting down."
        server.socket.close()
        
    except KeyboardInterrupt:
        print "^C received. Shutting down."
        server.socket.close()



if __name__=="__main__":
    try:
        Run()
    except KeyboardInterrupt:
        pass