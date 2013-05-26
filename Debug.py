#!/usr/bin/python

"""
Trying to channel debug output

debug levels (examples):
0 - non-repeating output (starting up, shutting down), error messages
1 - function return values
2 - lower debug data, function input values, intermediate info...
"""

dlevels = { "PlexConnect": 0, \
            "PlexGDM"    : 0, \
            "DNSServer"  : 1, \
            "WebServer"  : 1, \
            "XMLConverter" : 0, \
          }



def dprint(src, dlevel, *args):
    if (src in dlevels) == False or dlevel <= dlevels[src]:
        asc_args = list(args)
        
        for i,arg in enumerate(asc_args):
            if isinstance(asc_args[i], str):
                asc_args[i] = asc_args[i].decode('utf-8', 'replace')  # convert as utf-8 just in case
            if isinstance(asc_args[i], unicode):
                asc_args[i] = asc_args[i].encode('ascii', 'replace')  # back to ascii
        
        if len(asc_args)==0:
            print src,":"
        elif len(asc_args)==1:
            print src,":", asc_args[0]
        else:
            print src,":", asc_args[0].format(*asc_args[1:])



if __name__=="__main__":
    dprint('unknown', 0, "debugging {0}", __name__)
    dprint('unknown', 1, "level 1")
    
    dprint('PlexConnect', 0, "debugging {0}", 'PlexConnect')
    dprint('PlexConnect', 1, "level")