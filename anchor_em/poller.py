import asyncio
import logging
import time


from execplan import execution_plan

logging.basicConfig(level=logging.INFO)

CLE_FREQUENCY = 1

# logging setup
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("coap-server").setLevel(logging.DEBUG)


async def main(plan):

    # start execution queue
    while True:
        await plan.process()
        time.sleep(CLE_FREQUENCY)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main(execution_plan))
