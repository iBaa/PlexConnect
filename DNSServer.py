#!/usr/bin/python

"""
Source:
http://code.google.com/p/minidns/source/browse/minidns
"""

"""
Header
  7  6  5  4  3  2  1  0  7  6  5  4  3  2  1  0
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                      ID                       |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|QR|   Opcode  |AA|TC|RD|RA|   Z    |   RCODE   |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                    QDCOUNT                    |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                    ANCOUNT                    |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                    NSCOUNT                    |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                    ARCOUNT                    |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+

Query
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                                               |
/                     QNAME                     /
|                                               |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                     QTYPE                     |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                     QCLASS                    |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+

ResourceRecord
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                                               |
/                      NAME                     /
|                                               |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                      TYPE                     |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                     CLASS                     |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                      TTL                      |
|                                               |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                   RDLENGTH                    |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--|
|                                               |
/                     RDATA                     /
|                                               |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+

Source: http://doc-tcpip.org/Dns/named.dns.message.html
"""

import sys
import socket
import struct
import Queue  # inter process communication

from Debug import *  # dprint()



"""
 Hostname/DNS conversion
 Hostname: 'Hello.World'
 DNSdata:  '<len(Hello)>Hello<len(World)>World<NULL>
"""
def HostToDNS(Host):
    DNSdata = '.'+Host+'\0'  # python 2.6: bytearray()
    i=0
    while i<len(DNSdata)-1:
        next = DNSdata.find('.',i+1)
        if next==-1:
            next = len(DNSdata)-1
        DNSdata = DNSdata[:i] + chr(next-i-1) + DNSdata[i+1:]  # python 2.6: DNSdata[i] = next-i-1
        i = next
    
    return DNSdata

def DNSToHost(DNSdata, i=12):
    Host = ''
    while DNSdata[i]!='\0':
        nlen = ord(DNSdata[i])
        if nlen & 0xC0:
            i = ((ord(DNSdata[i]) & 0x3F)<<8) + ord(DNSdata[i+1])
        else:
            Host = Host + DNSdata[i+1:i+nlen+1]+'.'
            i+=nlen+1
    Host = Host[:-1]
    return Host

def DNSstring(DNSdata):
    i=0
    res = ''
    while DNSdata[i]!='\0':
        nlen = ord(DNSdata[i])
        res = res+'<'+str(nlen)+'>'+DNSdata[i+1:i+nlen+1]
        i+=nlen+1
    res = res+'<0>'
    return res



def printDNSPaket(paket):
    print "***Paket"
    print "ID {0:04x}".format((ord(data[0])<<8)+ord(data[1]))
    print "flags {0:02x} {1:02x}".format(ord(paket[2]), ord(paket[3]))
    print "OpCode "+str((ord(paket[2])>>3)&0x0F)
    print "RCode "+str((ord(paket[3])>>0)&0x0F)
    print "QDCOUNT "+str((ord(paket[4])<<8)+ord(paket[5]))
    print "ANCOUNT "+str((ord(paket[6])<<8)+ord(paket[7]))
    print "NSCOUNT "+str((ord(paket[8])<<8)+ord(paket[9]))
    print "ARCOUNT "+str((ord(paket[10])<<8)+ord(paket[11]))
    #print "Name: "+paket[12:]
    
    for i in range(len(paket)):
        print "%02x" % ord(paket[i]),
    print



def Run(cmdQueue, param):
    dinit(__name__, param)  # init logging, DNSServer process
    
    try:
        DNS = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        DNS.settimeout(5.0)
        DNS.bind(('',53))
    except Exception, e:
        dprint(__name__, 0, "Failed to create socket on UDP port 53: {0}", e)
        sys.exit(1)
    
    try:
        DNS_forward = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        DNS_forward.settimeout(5.0)
        DNS_forward.bind(('',49152))  # 49152 or above
        # todo: where to get free port from?
        # todo: do we need bind?
    except Exception, e:
        dprint(__name__, 0, "Failed to create socket on UDP port 49152: {0}", e)
        sys.exit(1)
    
    dprint(__name__, 0, "***")
    dprint(__name__, 0, "Starting up.")
    dprint(__name__, 1, "intercept "+param['HostToIntercept']+": "+param['IP_self'])
    dprint(__name__, 1, "forward other to higher level DNS: "+param['IP_DNSMaster'])
    dprint(__name__, 0, "***")
    
    try:
        while True:
            # check command
            try:
                cmd = cmdQueue.get_nowait()
                if cmd=='shutdown':
                    break
            
            except Queue.Empty:
                pass
            
            # do your work (with timeout)
            try:
                data, addr = DNS.recvfrom(1024)
                dprint(__name__, 1, "DNS request received!")
                dprint(__name__, 1, "Source: "+str(addr))
                #printDNSPaket(data)
                
                # analyse DNS request
                # todo: how about multi-query messages?
                opcode = (ord(data[2]) >> 3) & 0x0F # Opcode bits (query=0, inversequery=1, status=2)
                if opcode == 0:                     # Standard query
                    domain = DNSToHost(data, 12)
                    dprint(__name__, 1, "Domain: "+domain)
                
                paket=''
                if domain==param['HostToIntercept']:
                    dprint(__name__, 1, "***intercept request")
                    paket+=data[:2]         # 0:1 - ID
                    paket+="\x81\x80"       # 2:3 - flags
                    paket+=data[4:6]        # 4:5 - QDCOUNT - should be 1 for this code
                    paket+=data[4:6]        # 6:7 - ANCOUNT
                    paket+='\x00\x00'       # 8:9 - NSCOUNT
                    paket+='\x00\x00'       # 10:11 - ARCOUNT
                    paket+=data[12:]                                     # original query
                    paket+='\xc0\x0c'                                    # pointer to domain name/original query
                    paket+='\x00\x01\x00\x01\x00\x00\x00\x3c\x00\x04'    # response type, ttl and resource data length -> 4 bytes
                    paket+=str.join('',map(lambda x: chr(int(x)), param['IP_self'].split('.'))) # 4bytes of IP
                    dprint(__name__, 1, "-> DNS response: "+param['IP_self'])
                
                else:
                    dprint(__name__, 1, "***forward request")
                    DNS_forward.sendto(data, (param['IP_DNSMaster'], 53))
                    paket, addr_master = DNS_forward.recvfrom(1024)
                    # todo: double check: ID has to be the same!
                    # todo: spawn thread to wait in parallel
                    dprint(__name__, 1, "-> DNS response from higher level")
                
                #print "-> respond back:"
                #printPaket(paket)
                
                # todo: double check: ID has to be the same!
                DNS.sendto(paket, addr)
            
            except socket.timeout:
                pass
            
            except socket.error as e:
                dprint(__name__, 1, "Warning: DNS error ({0}): {1}", e.errno, e.strerror)
            
    except KeyboardInterrupt:
        dprint(__name__, 0, "^C received.")
    finally:
        dprint(__name__, 0, "Shutting down.")
        DNS.close()
        DNS_forward.close()



if __name__ == '__main__':
    cmd = Queue.Queue()\
    
    param = {}
    param['IP_self'] = '192.168.178.20'
    param['IP_DNSMaster'] = '8.8.8.8'
    param['HostToIntercept'] = 'trailers.apple.com'
    
    Run(cmd, param)