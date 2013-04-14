#!/usr/bin/python

"""
Source: a couple of lines from "the internet" - stackoverflow.com and such
"""
import sys
import string, cgi, time
from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer


class MyHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            # reply with requested file from "assets"
            # todo: path, security, interface to PMS
            f = open(curdir + sep + "assets" + sep + self.path)  # attention - opening every file to the internet
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(f.read())
            f.close()
            return
            
        except IOError:
            self.send_error(404,"File Not Found: %s" % self.path)


#Protocol     = "HTTP/1.0"
# todo: IP, port

try:
    server = HTTPServer(('',80), MyHandler)

    sa = server.socket.getsockname()
    print "Serving HTTP on", sa[0], "port", sa[1], "..."
    server.serve_forever()
except KeyboardInterrupt:
    print "^C received. Shutting down."
    server.socket.close()