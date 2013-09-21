#!/usr/bin/env python

from Debug import * #dprint()
from urllib import FancyURLopener
from urllib2 import urlopen

class BasicAuth(FancyURLopener):
    def setpasswd(self, user, passwd):
        self.__user = user
        self.__passwd = passwd
        self.__retries = 0
    
    def prompt_user_passwd(self, host, realm):
        if self.__retries<1:
            self.__retries += 1
            return self.__user, self.__passwd
        else:
            raise IOError('Auth Failed!')
            return

def getExternalIP():
    #Function to get gateway ip    
    dprint(__name__, 0, "Get External IP")
    ext_IP = urlopen('http://ip.42.pl/raw').read()
    dprint(__name__, 0, "External IP: {0}", ext_IP)
    return ext_IP
    
def getInternalIP():
    #Function to get ip of PlexConnect
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('1.2.3.4', 1000))
    int_IP = s.getsockname()[0]
    return int_IP
