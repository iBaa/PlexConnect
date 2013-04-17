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

import Settings

Name_intercept = "trailers.apple.com"



def printDNSPaket(paket):
    print "***Paket"
    print "ID {:04x}".format((ord(data[0])<<8)+ord(data[1]))
    print "flags {:02x} {:02x}".format(ord(paket[2]), ord(paket[3]))
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



KeepRunning = True
def SetKeepRunning(in_KeepRunning):
    KeepRunning = in_KeepRunning



def Run():
    try:
        DNS = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        DNS.bind(('',53))
    except Exception, e:
        print "Failed to create socket on UDP port 53:", e
        sys.exit(1)
    
    try:
        DNS_forward = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        DNS_forward.bind(('',49152))  # 49152 or above
        # todo: where to get free port from?
        # todo: do we need bind?
    except Exception, e:
        print "Failed to create socket on UDP port 49152:", e
        sys.exit(1)
    
    print "***"
    print "DNS Server"
    print "intercept: "+Name_intercept
    print "forward other to higher level DNS: "+Settings.getIP_DNSmaster()
    print "***"
   
    try:
        while KeepRunning:
            data, addr = DNS.recvfrom(1024)
            print "DNS request received!"
            print "Source: "+str(addr)
            #printDNSPaket(data)
            
            # analyse DNS request
            # todo: how about multi-query messages?
            opcode = (ord(data[2]) >> 3) & 0x0F # Opcode bits (query=0, inversequery=1, status=2)
            if opcode == 0:                     # Standard query
                domain=''
                i=12
                while data[i]!='\0':
                    nlen = ord(data[i])
                    domain+=data[i+1:i+nlen+1]+'.'
                    i+=nlen+1
                domain=domain[:-1] 
                print "Domain: "+domain
            
            paket=''
            if domain==Name_intercept:
                print "***intercept request"
                paket+=data[:2]         # 0:1 - ID
                paket+="\x81\x80"       # 2:3 - flags
                paket+=data[4:6]        # 4:5 - QDCOUNT - should be 1 for this code
                paket+=data[4:6]        # 6:7 - ANCOUNT
                paket+='\x00\x00'       # 8:9 - NSCOUNT
                paket+='\x00\x00'       # 10:11 - ARCOUNT
                paket+=data[12:]                                     # original query
                paket+='\xc0\x0c'                                    # pointer to domain name/original query
                paket+='\x00\x01\x00\x01\x00\x00\x00\x3c\x00\x04'    # response type, ttl and resource data length -> 4 bytes
                paket+=str.join('',map(lambda x: chr(int(x)), Settings.getIP_PMS().split('.'))) # 4bytes of IP
                print "-> DNS response: IP_PMS"
            
            else:
                print "***forward request"
                DNS_forward.sendto(data, (Settings.getIP_DNSmaster(), 53))
                paket, addr_master = DNS_forward.recvfrom(1024)
                # todo: double check: ID has to be the same!
                # todo: spawn thread to wait in parallel
                print "-> DNS response from higher level"
            
            #print "-> respond back:"
            #printPaket(paket)
            
            # todo: double check: ID has to be the same!
            DNS.sendto(paket, addr)
        
        print "DNSServer: Shutting down."
        DNS.close()
        DNS_forward.close()
    
    except KeyboardInterrupt:
        print "^C received. Shutting down."
        DNS.close()
        DNS_forward.close()



if __name__ == '__main__':
    try:
        Run()
    except KeyboardInterrupt:
        pass