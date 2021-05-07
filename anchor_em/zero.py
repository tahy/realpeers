# import socket
import logging
# from zeroconf import ServiceBrowser, Zeroconf
from time import sleep
import subprocess
from db import objects as db_objects, AnchorModel


ZERO_CLE_FREQUENCY = 3

import logging
logging.basicConfig(level=logging.DEBUG)

# class ZeroListener:
#
#     def remove_service(self, zeroconf_, type_, name):
#         print(zeroconf)
#         print("Service %s removed" % (name,))
#
#     def add_service(self, zeroconf_, type_, name):
#         info = zeroconf.get_service_info(type_, name)
#         host_ip = socket.inet_ntoa(info.addresses[0])
#         print(host_ip)
#         with db_objects.allow_sync():
#             anchors = AnchorModel.select().where(AnchorModel.ip_address == host_ip)
#             if not anchors:
#                 AnchorModel.create(ip_address=host_ip)
#         print("Service %s added, service info: %s" % (name, info))


# zeroconf = Zeroconf()
# browser = ServiceBrowser(zeroconf, "_http._tcp.local.", ZeroListener())

def avahi():

    command = "avahi-browse -r -t _ortho._udp "
    print("Start %s" % command)
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.debug("Result encoded: %s" % result.stdout)
    print(result.stdout)
    print(result.stderr)



print("Start zero container")
while True:
    avahi()
    sleep(ZERO_CLE_FREQUENCY)

