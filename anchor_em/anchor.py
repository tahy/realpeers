import asyncio
import aiocoap.resource as resource
import aiocoap
import logging
import socket

from zeroconf import ServiceInfo, Zeroconf

from config import config
from report import ConfigGetReport, StateGetReport, PopQueueGetReport, \
    ConfigPutReport, StatePutReport

# logging setup
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("coap-server").setLevel(logging.DEBUG)


def zeroconf_rigister_service():
    hostname = socket.gethostname()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('google.com', 0))
    hostip = s.getsockname()[0]
    # print("hostname = " + hostname)
    # print("ip = " + hostip)
    desc = {'name': hostname}

    info = ServiceInfo(
        type_="_http._tcp.local.",
        name="Anchor_service#%s._http._tcp.local." % config.ID,
        addresses=[socket.inet_aton(hostip)],
        port=5683,
        properties=desc,
        server="ash-2.local.",
    )
    zeroconf = Zeroconf()
    try:
        print("Registering " + hostname + "...")
        zeroconf.register_service(info)
    except Exception as e:
        raise e
    finally:
        pass
        # zeroconf.close()


class AnchorResource(resource.Resource):
    get_report_class = None
    put_report_class = None

    async def render(self, request):
        m = getattr(self, '%s_report_class' % str(request.code).lower(), None)
        if not m:
            raise resource.error.UnallowedMethod()
        return await super().render(request)

    async def render_get(self, request):
        report = self.get_report_class(request.payload)
        return aiocoap.Message(payload=report.render_frame())

    async def render_put(self, request):
        report = self.put_report_class(request.payload)
        return aiocoap.Message(code=aiocoap.CHANGED, payload=report.render_frame())


class AnchorConfigResource(AnchorResource):
    get_report_class = ConfigGetReport
    put_report_class = ConfigPutReport


class AnchorStateResource(AnchorResource):
    get_report_class = StateGetReport
    put_report_class = StatePutReport


class PopQueueResource(AnchorResource):
    get_report_class = PopQueueGetReport


def main():
    # announcing zeroconf service
    zeroconf_rigister_service()

    # register coap server
    root = resource.Site()
    root.add_resource(['anchor-config'], AnchorConfigResource())
    root.add_resource(['anchor-state'], AnchorStateResource())
    root.add_resource(['popqueue'], PopQueueResource())
    asyncio.Task(aiocoap.Context.create_server_context(root))
    asyncio.get_event_loop().run_forever()


if __name__ == "__main__":
    main()
