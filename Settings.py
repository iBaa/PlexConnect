#!/usr/bin/env python

import sys
from os import sep
import ConfigParser

from Debug import *  # dprint()



"""
Global Settings...
PMS: plexgdm, ip_pms, port_pms
DNS: ip_dnsmaster - IP of Router, ISP's DNS, ... [dflt: google public DNS]
IP_self: enable_plexconnect_autodetect, ip_plexconnect - manual override for VPN usage
Intercept: Trailers-trailers.apple.com, WSJ-secure.marketwatch.com, iMovie-www.icloud.com
HTTP: port_webserver - override when using webserver + forwarding to PlexConnect
HTTPS: port_ssl, certfile, enable_webserver_ssl - configure SSL portion or webserver
"""
g_settings = { \
    'enable_plexgdm'  :('True', 'False'), \
    'ip_pms'          :('192.168.178.10',), \
    'port_pms'        :('32400',), \
    \
    'enable_dnsserver':('True', 'False'), \
    'port_dnsserver'  :('53',), \
    'ip_dnsmaster'    :('8.8.8.8',), \
    'prevent_atv_update'           :('True', 'False'), \
    \
    'enable_plexconnect_autodetect':('True', 'False'), \
    'ip_plexconnect'  :('0.0.0.0',), \
    'hosttointercept' :('trailers.apple.com',), \
    \
    'port_webserver'  :('80',), \
    'enable_webserver_ssl'         :('True', 'False'), \
    'port_ssl'        :('443',), \
    'certfile'        :('./assets/certificates/trailers.pem',), \
    \
    'loglevel'        :('Normal', 'High', 'Off'), \
    'logpath'         :('.',), \
    \
    'hosttointercept' :('trailers.apple.com',), \
    }



class CSettings():
    def __init__(self):
        dprint(__name__, 1, "init class CSettings")
        self.cfg = None
        self.section = 'PlexConnect'
        self.loadSettings()
        self.checkSection()
    
    
    
    # load/save config
    def loadSettings(self):
        dprint(__name__, 1, "load settings")
        # options -> default
        dflt = {}
        for opt in g_settings:
            dflt[opt] = g_settings[opt][0]
        
        # load settings
        self.cfg = ConfigParser.SafeConfigParser()
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
        
        for opt in g_settings:
            if not self.cfg.has_option(self.section, opt):
                modify = True
                self.cfg.set(self.section, opt, g_settings[opt][0])
                dprint(__name__, 0, "add option {0}={1}", opt, g_settings[opt][0])
                
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
    
    Settings.saveSettings()
    del Settings
