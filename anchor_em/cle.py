import asyncio
import logging
import time

from aiocoap import Context
from collections import deque
from functools import partial

from client import set_config, set_state, popqueue
from db import objects as db_objects, AnchorModel
from decawave import AnchorConfigurationFrame, AnchorStateFrame, CPPTXFrame, CPPRXFrame, BlinkFrame

logging.basicConfig(level=logging.INFO)

CLE_FREQUENCY = 1

# logging setup
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("coap-server").setLevel(logging.DEBUG)


class Job:
    def __init__(self, work, latency=1):
        self.work = work
        self.latency = latency
        self._counter = latency

    def its_time(self):
        self._counter -= 1
        return bool(self._counter == 0)

    def need_continue(self):
        return bool(self._counter)


class RegularJob(Job):

    def its_time(self):
        if super().its_time():
            self._counter = self.latency
            return True


class ExecutionPlan:
    queue = []

    def __init__(self, job_list):
        self.queue = deque(job_list)

    def add_job(self, job):
        self.queue.append(job)

    async def process(self):
        job = self.queue.popleft()
        if job.its_time():
            await job.work()

        if job.need_continue():
            self.queue.append(job)


async def set_config_job(anchor):
    # print(anchor.ip_address)
    response = await set_config(anchor.ip_address, AnchorConfigurationFrame().to_binary())
    print('Set config result : %s\n%r\n' % (response.code, response.payload))


async def set_state_job(anchor):
    # print(anchor.ip_address)
    response = await set_state(anchor.ip_address, AnchorStateFrame(bytes([1])).to_binary())
    print('Set state result : %s\n%r\n' % (response.code, response.payload))


async def popqueue_job(anchor):
    # print(anchor.ip_address)
    response = await popqueue(anchor.ip_address)
    print('Popqueue result: %s\n%r\n' % (response.code, response.payload))
    if response.payload[0] == 48:  # 0x30
        frame = CPPTXFrame(response.payload)
        print(frame)
    if response.payload[0] == 49:  # 0x31
        frame = CPPRXFrame(response.payload)
        print(frame)
    if response.payload[0] == 50:  # 0x32
        frame = BlinkFrame(response.payload)
        print(frame)


# collect anchor list
async def init_job_list():
    job_list = []
    anchor_list = await db_objects.execute(AnchorModel.select())
    for anchor in anchor_list:
        job_list.append(Job(partial(set_config_job, anchor)))
        job_list.append(Job(partial(set_state_job, anchor)))
        job_list.append(RegularJob(partial(popqueue_job, anchor), 5))
    return job_list


async def main():
    plan = ExecutionPlan(await init_job_list())
    while True:
        await plan.process()
        time.sleep(CLE_FREQUENCY)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
