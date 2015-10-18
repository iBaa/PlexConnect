#!/usr/bin/env python

import sys
from os import sep
import ConfigParser
import re

from Debug import *  # dprint()



"""
Global Settings...
syntax: 'setting': ('default', 'regex to validate')

PMS: plexgdm, ip_pms, port_pms
DNS: ip_dnsmaster - IP of Router, ISP's DNS, ... [dflt: google public DNS]
IP_self: enable_plexconnect_autodetect, ip_plexconnect - manual override for VPN usage
Intercept: Trailers-trailers.apple.com, WSJ-secure.marketwatch.com, iMovie-www.icloud.com
HTTP: port_webserver - override when using webserver + forwarding to PlexConnect
HTTPS: port_ssl, certfile, enable_webserver_ssl - configure SSL portion or webserver
"""
g_settings = [
    ('enable_plexgdm'  , ('True', '((True)|(False))')),
    ('ip_pms'          , ('192.168.178.10', '([0-9]{1,3}\.){3}[0-9]{1,3}')),
    ('port_pms'        , ('32400', '[0-9]{1,5}')),
    \
    ('enable_dnsserver', ('True', '((True)|(False))')),
    ('port_dnsserver'  , ('53', '[0-9]{1,5}')),
    ('ip_dnsmaster'    , ('8.8.8.8', '([0-9]{1,3}\.){3}[0-9]{1,3}')),
    ('prevent_atv_update'           , ('True', '((True)|(False))')),
    ('intercept_atv_icon', ('True', '((True)|(False))')),
    ('icon', ('com.apple.imovietheatre.appletv', '[a-zA-Z0-9_.-]+')),
    \
    ('enable_plexconnect_autodetect', ('True', '((True)|(False))')),
    ('ip_plexconnect'  , ('0.0.0.0', '([0-9]{1,3}\.){3}[0-9]{1,3}')),
    ('hosttointercept' , ('trailers.apple.com', '[a-zA-Z0-9_.-]+')),
    \
    ('port_webserver'  , ('80', '[0-9]{1,5}')),
    ('enable_webserver_ssl'         , ('True', '((True)|(False))')),
    ('port_ssl'        , ('443', '[0-9]{1,5}')),
    ('certfile'        , ('./assets/certificates/trailers.pem', '.+.pem')),
    \
    ('allow_gzip_atv'              , ('False', '((True)|(False))')),
    ('allow_gzip_pmslocal'         , ('False', '((True)|(False))')),
    ('allow_gzip_pmsremote'        , ('True', '((True)|(False))')),
    \
    ('loglevel'        , ('Normal', '((Off)|(Normal)|(High))')),
    ('logpath'         , ('.', '.+')),
    ]



class CSettings():
    def __init__(self):
        dprint(__name__, 1, "init class CSettings")
        self.cfg = ConfigParser.SafeConfigParser()
        self.section = 'PlexConnect'
        
        # set option for fixed ordering
        self.cfg.add_section(self.section)
        for (opt, (dflt, vldt)) in g_settings:
            self.cfg.set(self.section, opt, '\0')
        
        self.loadSettings()
        self.checkSection()
    
    
    
    # load/save config
    def loadSettings(self):
        dprint(__name__, 1, "load settings")
        self.cfg.read(self.getSettingsFile())
    
    def saveSettings(self):
        dprint(__name__, 1, "save settings")
        f = open(self.getSettingsFile(), 'wb')
        self.cfg.write(f)
        f.close()
    
    def getSettingsFile(self):
        return sys.path[0] + sep + "Settings.cfg"
    
    def checkSection(self):
        modify = False
        # check for existing section
        if not self.cfg.has_section(self.section):
            modify = True
            self.cfg.add_section(self.section)
            dprint(__name__, 0, "add section {0}", self.section)
        
        for (opt, (dflt, vldt)) in g_settings:
            setting = self.cfg.get(self.section, opt)
            if setting=='\0':
                # check settings - add if new
                modify = True
                self.cfg.set(self.section, opt, dflt)
                dprint(__name__, 0, "add setting {0}={1}", opt, dflt)
            
            elif not re.search('\A'+vldt+'\Z', setting):
                # check settings - default if unknown
                modify = True
                self.cfg.set(self.section, opt, dflt)
                dprint(__name__, 0, "bad setting {0}={1} - set default {2}", opt, setting, dflt)
        
        # save if changed
        if modify:
            self.saveSettings()
    
    
    
    # access/modify PlexConnect settings
    def getSetting(self, option):
        dprint(__name__, 1, "getsetting {0}={1}", option, self.cfg.get(self.section, option))
        return self.cfg.get(self.section, option)



if __name__=="__main__":
    Settings = CSettings()
    
    option = 'enable_plexgdm'
    print Settings.getSetting(option)
    
    option = 'enable_dnsserver'
    print Settings.getSetting(option)
    
    del Settings
