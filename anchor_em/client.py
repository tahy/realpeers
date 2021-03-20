import asyncio
import logging
import time

from aiocoap import Context, Message, GET, PUT

from decawave import AnchorConfigurationFrame, AnchorStateFrame, CPPTXFrame, CPPRXFrame, BlinkFrame

logging.basicConfig(level=logging.INFO)

CLE_FREQUENCY = 5


async def main():
    protocol = await Context.create_client_context()

    while True:
        request = Message(code=GET, uri='coap://anchor1/anchor-state')
        try:
            response = await protocol.request(request).response
        except Exception as e:
            print('Failed to fetch resource:')
            print(e)
        else:
            print('Result : %s\n%r' % (response.code, response.payload))

        request = Message(code=PUT, payload=AnchorStateFrame(bytes([1])).to_binary(),
                          uri='coap://anchor1/anchor-state')
        try:
            response = await protocol.request(request).response
        except Exception as e:
            print('Failed to fetch resource:')
            print(e)
        else:
            print('Result: %s\n%r' % (response.code, response.payload))

        request = Message(code=GET, uri='coap://anchor1/anchor-config')
        try:
            response = await protocol.request(request).response
        except Exception as e:
            print('Failed to fetch resource:')
            print(e)
        else:
            print('Result: %s\n%r' % (response.code, response.payload))

        request = Message(code=PUT, payload=AnchorConfigurationFrame().to_binary(),
                          uri='coap://anchor1/anchor-config')
        try:
            response = await protocol.request(request).response
        except Exception as e:
            print('Failed to fetch resource:')
            print(e)
        else:
            print('Result: %s\n%r' % (response.code, response.payload))

        request = Message(code=GET, uri='coap://anchor1/popqueue')
        try:
            response = await protocol.request(request).response
        except Exception as e:
            print('Failed to fetch resource:')
            print(e)
        else:
            # print('Result: %s\n%r' % (response.code, response.payload))
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
