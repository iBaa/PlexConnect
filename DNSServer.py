from dnslib.intercept import InterceptResolver
import dnslib.server
from Debug import *


class DNSServer():
    def __init__(self, param):

        cfg = param['CSettings']
        cfg_IP_self = param['IP_self']

        if cfg.getSetting('use_custom_dns_bind_ip') == "True":
            intercept_ip = cfg.getSetting('custom_dns_bind_ip')
        else:
            intercept_ip = cfg_IP_self

        cfg_Port_DNSServer = int(cfg.getSetting('port_dnsserver'))
        if not cfg_Port_DNSServer:
            cfg_Port_DNSServer = 53
        cfg_IP_DNSMaster = cfg.getSetting('ip_dnsmaster')

        intercept = [param['HostToIntercept']]
        restrain = []
        if cfg.getSetting('intercept_atv_icon') == 'True':
            intercept.append('a1.phobos.apple.com')
            dprint(__name__, 0, "Intercept Atv Icon: Enabled")
        if cfg.getSetting('prevent_atv_update') == 'True':
            restrain = ['mesu.apple.com', 'appldnld.apple.com',
                        'appldnld.apple.com.edgesuite.net']
            dprint(__name__, 0, "Prevent Atv Update: Enabled")

        dprint(__name__, 0, "***")
        dprint(__name__, 0,
               f"DNSServer: Serving DNS on {cfg_IP_self} port {cfg_Port_DNSServer}.")
        dprint(__name__, 1, f"intercept: {intercept} => {intercept_ip}")
        dprint(__name__, 1, f"restrain: {restrain} => NXDOMAIN")
        dprint(__name__, 1,
               f"forward other to higher level DNS: {cfg_IP_DNSMaster}")
        dprint(__name__, 0, "***")

        intercept_records = [f"{i} 300 IN A {intercept_ip}" for i in intercept]

        resolver = InterceptResolver(
            address=cfg_IP_DNSMaster,
            port=53,
            intercept=intercept_records,
            nxdomain=restrain,
            skip=[],
            forward=[],
            all_qtypes=True,
            ttl="30s",
            timeout=30
        )
        logger = dnslib.server.DNSLogger(prefix=False)
        self.server = dnslib.server.DNSServer(
            resolver, address=cfg_IP_self, port=cfg_Port_DNSServer, logger=logger,
            tcp=False)

    def start_thread(self):
        self.server.start_thread()

    def stop(self):
        self.server.stop()

    def isAlive(self):
        self.server.isAlive()
