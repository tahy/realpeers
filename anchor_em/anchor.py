import asyncio
import logging

import aiocoap.resource as resource
import aiocoap

from decawave import DecawaveRequest, DecawaveReport, CPPUWBFrame


# frame = CPPUWBFrame(b"123456789012345678")
# # print(frame.fields)
# frame2 = CPPUWBFrame()
# print(frame2.fields)
# print(dir(frame))
# print(frame.frame_ctrl)

#
# print(frame.to_binary())
# print(frame2.to_binary())
# print(frame2.frame_ctrl_raw)
# print(frame2.frame_ctrl_hex)
# print(frame2.frame_ctrl)
# print(frame2.dest_addr)
# print(frame2.fn_cd_hex)
# print(frame2.src_addr_dec)
# print(frame2.src_addr_hex)
# print(frame2.src_addr)

# logging setup
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("coap-server").setLevel(logging.DEBUG)


class AnchorResource(resource.Resource):

    async def render_get(self, request):
        decawave_request = DecawaveRequest(bin_frame=request.payload)
        decawave_report = DecawaveReport(decawave_request)
        return aiocoap.Message(payload=decawave_report.render_frame())


def main():
    root = resource.Site()
    root.add_resource(['main'], AnchorResource())
    asyncio.Task(aiocoap.Context.create_server_context(root))
    asyncio.get_event_loop().run_forever()


if __name__ == "__main__":
    main()
