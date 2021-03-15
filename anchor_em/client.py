import asyncio
import logging
import time

from aiocoap import Context, Message, GET, PUT

from decawave import CPPUWBFrame, AnchorConfigurationFrame

logging.basicConfig(level=logging.INFO)

CLE_FREQUENCY = 5


async def main():
    protocol = await Context.create_client_context()

    while True:
        # create CCP frame
        frames = CPPUWBFrame(), AnchorConfigurationFrame()

        for frame in frames:
            request = Message(code=GET, payload=frame.to_binary(), uri='coap://anchor/main')

            try:
                response = await protocol.request(request).response
            except Exception as e:
                print('Failed to fetch resource:')
                print(e)
            else:
                print('Result: %s\n%r' % (response.code, response.payload))

            time.sleep(CLE_FREQUENCY)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
