import socket

from zeroconf import ServiceBrowser, Zeroconf
from time import sleep

from db import objects as db_objects, AnchorModel
ZERO_CLE_FREQUENCY = 1


class ZeroListener:

    def remove_service(self, zeroconf_, type_, name):
        print(zeroconf)
        print("Service %s removed" % (name,))

    def add_service(self, zeroconf_, type_, name):
        info = zeroconf.get_service_info(type_, name)
        host_ip = socket.inet_ntoa(info.addresses[0])
        print(host_ip)
        with db_objects.allow_sync():
            anchors = AnchorModel.select().where(AnchorModel.ip_address == host_ip)
            if not anchors:
                AnchorModel.create(ip_address=host_ip)
        print("Service %s added, service info: %s" % (name, info))


zeroconf = Zeroconf()
browser = ServiceBrowser(zeroconf, "_http._tcp.local.", ZeroListener())
try:
    while True:
        sleep(ZERO_CLE_FREQUENCY)
finally:
    zeroconf.close()
