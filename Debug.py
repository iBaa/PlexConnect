#!/usr/bin/python

"""
Trying to channel debug output

debug levels (examples):
0 - non-repeating output (starting up, shutting down), error messages
1 - function return values
2 - lower debug data, function input values, intermediate info...
"""

dlevels = { "PlexConnect": 0, \
            "DNSServer"  : 1, \
            "WebServer"  : 1, \
            "XMLConverter" : 0, \
          }



def dprint(src, dlevel, str, *args):
    if (src in dlevels) == False or dlevel <= dlevels[src]:
        print src,":", str.format(*args)



if __name__=="__main__":
    dprint('unknown', 0, "debugging {0}", __name__)
    dprint('unknown', 1, "level 1")
    
    dprint('PlexConnect', 0, "debugging {0}", 'PlexConnect')
    dprint('PlexConnect', 1, "level")