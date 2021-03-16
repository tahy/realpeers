import asyncio
import logging

import aiocoap.resource as resource
import aiocoap

from report import ConfigGetReport, StateGetReport, PopQueueGetReport

# logging setup
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("coap-server").setLevel(logging.DEBUG)


class AnchorResource(resource.Resource):
    get_report_class = None
    put_report_class = None

    def get_report_data(self):
        raise NotImplementedError

    def put_report_data(self):
        raise NotImplementedError

    async def render(self, request):
        method = str(request.code).lower()
        if method == "get":
            if not self.get_report_class:
                raise resource.error.UnallowedMethod()
        if method == "put":
            if not self.put_report_class:
                raise resource.error.UnallowedMethod()
        return await super().render(request)

    async def render_get(self, request):
        if self.get_report_class:
            decawave_report = self.get_report_class()
            return aiocoap.Message(payload=decawave_report.render_frame())
        else:
            raise Exception("Unknown coap method!")

    async def render_put(self, request):
        print('PUT payload: %s' % request.payload)
        self.set_content(request.payload)
        return aiocoap.Message(code=aiocoap.CHANGED, payload=self.content)


class AnchorConfig(AnchorResource):
    get_report_class = ConfigGetReport
    put_report_class = ConfigPutReport


class AnchorState(AnchorResource):
    get_report_class = StateGetReport
    put_report_class = StatePutReport


class PopQueue(AnchorResource):
    get_report_class = PopQueueGetReport


def main():
    root = resource.Site()
    root.add_resource(['anchor-config'], AnchorConfig())
    root.add_resource(['popqueue'], AnchorState())
    root.add_resource(['anchor-state'], PopQueue())
    asyncio.Task(aiocoap.Context.create_server_context(root))
    asyncio.get_event_loop().run_forever()


if __name__ == "__main__":
    main()
