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
            "Settings"   : 0, \
            "ATVSettings": 0, \
          }



import time



g_logfile = ''
g_loglevel = 0

def dinit(src, param, newlog=False):    
    if 'LogFile' in param:
        global g_logfile
        g_logfile = param['LogFile']
        
    if 'LogLevel' in param:
        global g_loglevel
        g_loglevel = { "Normal": 0,"High": 2 }.get(param['LogLevel'], 0)
    
    if not g_logfile=='' and newlog:
        f = open(g_logfile, 'w')
        f.close()
        
    dprint(src, 0, "started: {0}", time.strftime("%H:%M:%S"))



def dprint(src, dlevel, *args):
    if (src in dlevels) == False or dlevel <= dlevels[src] or \
       dlevel <= g_loglevel:
        asc_args = list(args)
        
        for i,arg in enumerate(asc_args):
            if isinstance(asc_args[i], str):
                asc_args[i] = asc_args[i].decode('utf-8', 'replace')  # convert as utf-8 just in case
            if isinstance(asc_args[i], unicode):
                asc_args[i] = asc_args[i].encode('ascii', 'replace')  # back to ascii
        
        # print to file (if filename defined)
        if not g_logfile=='':
            f = open(g_logfile, 'a')
            f.write(time.strftime("%H:%M:%S "))
            if len(asc_args)==0:
                f.write(src+":\n")
            elif len(asc_args)==1:
                f.write(src+": "+asc_args[0]+"\n")
            else:
                f.write(src+": "+asc_args[0].format(*asc_args[1:])+"\n")
            f.close()
        
        # print to terminal window
        if (src in dlevels) == False or dlevel <= dlevels[src]:
            if len(asc_args)==0:
                print src+":"
            elif len(asc_args)==1:
                print src+": "+asc_args[0]
            else:
                print src+": "+asc_args[0].format(*asc_args[1:])



if __name__=="__main__":
    dinit('Debug', {'LogFile':'Debug.log'}, True)  # True -> new file
    dinit('unknown', {'Logfile':'Debug.log'})  # False/Dflt -> append to file
    
    dprint('unknown', 0, "debugging {0}", __name__)
    dprint('unknown', 1, "level 1")
    
    dprint('PlexConnect', 0, "debugging {0}", 'PlexConnect')
    dprint('PlexConnect', 1, "level")