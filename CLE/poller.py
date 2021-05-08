import asyncio
import getopt
import logging
import sys
import time

from CLE.config import config
from CLE.execplan import execution_plan
from CLE.ds.sql import init_db, async_session as session


logging.basicConfig(level=logging.INFO)

CLE_FREQUENCY = 1

# logging setup
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("coap-server").setLevel(logging.DEBUG)


async def main():
    await init_db()
    argument_list = sys.argv[1:]
    options = "hc:"
    long_options = ["help", "config=", ]

    try:
        arguments, values = getopt.getopt(argument_list, options, long_options)
        for currentArgument, currentValue in arguments:
            if currentArgument in ("-h", "--help"):
                print("Diplaying Help надо потом дописать справку")
            elif currentArgument in ("-c", "--config"):
                print("Config file path: %s" % currentValue)
                # set poller config
                config.config_file = currentValue
                config.load_from_yml()

    except getopt.error as err:
        print(str(err))

    while True:
        await execution_plan.process()
        time.sleep(CLE_FREQUENCY)


def run():
    asyncio.get_event_loop().run_until_complete(main())


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
