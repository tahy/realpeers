import asyncio
import logging
import time

from aiocoap import Context, Message, GET, PUT

from decawave import AnchorConfigurationFrame, AnchorStateFrame, CPPTXFrame, CPPRXFrame, BlinkFrame

logging.basicConfig(level=logging.INFO)

CLE_FREQUENCY = 5


def catch_exception(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            print('Failed to fetch resource:')
            print(e)
    return wrapper


@catch_exception
async def get_state(ip_addr):
    request = Message(code=GET, uri='coap://%s/anchor-state' % ip_addr)
    protocol = await Context.create_client_context()
    return await protocol.request(request).response


@catch_exception
async def set_state(ip_addr, state):
    request = Message(code=PUT, payload=state, uri='coap://%s/anchor-state' % ip_addr)
    protocol = await Context.create_client_context()
    return await protocol.request(request).response


@catch_exception
async def get_config(ip_addr):
    request = Message(code=GET, uri='coap://%s/anchor-config' % ip_addr)
    protocol = await Context.create_client_context()
    return await protocol.request(request).response


@catch_exception
async def set_config(ip_addr, config):
    request = Message(code=GET, uri='coap://%s/anchor-config' % ip_addr)
    protocol = await Context.create_client_context()
    return await protocol.request(request).response


@catch_exception
async def popqueue(ip_addr):
    request = Message(code=GET, uri='coap://%s/popqueue' % ip_addr)
    protocol = await Context.create_client_context()
    return await protocol.request(request).response


async def main():
    """example code for usage coap client for anchors"""

    anchor_ip = "192.168.160.4"
    while True:

        response = await get_state(anchor_ip)
        print('Get state result : %s\n%r\n' % (response.code, response.payload))

        response = await set_state(anchor_ip,
                                   AnchorStateFrame(bytes([1])).to_binary())
        print('Set state result : %s\n%r\n' % (response.code, response.payload))

        response = await get_config(anchor_ip)
        print('Get config result : %s\n%r\n' % (response.code, response.payload))

        response = await set_config(anchor_ip,
                                    AnchorConfigurationFrame().to_binary())
        print('Set config result : %s\n%r\n' % (response.code, response.payload))

        response = await popqueue(anchor_ip)
        print('Popqueue result: %s\n%r\n' % (response.code, response.payload))
        if response.payload[0] == 48:            # 0x30
            frame = CPPTXFrame(response.payload)
            print(frame)
        if response.payload[0] == 49:            # 0x31
            frame = CPPRXFrame(response.payload)
            print(frame)
        if response.payload[0] == 50:            # 0x32
            frame = BlinkFrame(response.payload)
            print(frame)

        time.sleep(CLE_FREQUENCY)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
