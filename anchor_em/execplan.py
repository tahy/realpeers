import json

from collections import deque
from importlib import import_module

from client import set_config, set_state, popqueue
from config import ANCHOR_STATE_IDLE, ANCHOR_STATE_CONFIGURED, ANCHOR_STATE_WORKING
from db import objects as db_objects, AnchorModel, DefaultConfigModel, AnchorReportModel, JobModel
from decawave import AnchorConfigurationFrame, AnchorStateFrame, CPPTXFrame, CPPRXFrame, BlinkFrame
from rabbit import publish as rabbit_publish
from solver import solve
from influxdb import publish as influx_publish


class Job:
    """Задача, имеет рабочую нагрузку в виде метода work и задержку
    latency - число системных тиков общего плана до выполнения задачи
    """
    plan = None

    def __init__(self, latency=1, parameters=None):
        self.latency = latency
        self.parameters = parameters
        self._counter = latency

    @classmethod
    def set_plan(cls, plan):
        cls.plan = plan

    def its_time(self):
        self._counter -= 1
        return bool(self._counter == 0)

    def need_continue(self):
        return bool(self._counter)

    def work(self):
        raise NotImplementedError


class RegularJob(Job):
    """
    Регулярная задача, в отличие от обычной обновляет
    свой счетчик тиков на latency после выполнения рабочей нагрузки
    """
    def its_time(self):
        if super().its_time():
            self._counter = self.latency
            return True


class InitAnchors(Job):
    """Собираем анкоры из базы"""

    async def work(self):
        anchor_list = await db_objects.execute(AnchorModel.select())
        for anchor in anchor_list:
            if anchor.state == ANCHOR_STATE_IDLE:
                self.plan.add_job(ConfigureAnchorJob(anchor))
            if anchor.state == ANCHOR_STATE_CONFIGURED:
                self.plan.add_job(SetStateAnchorJob(anchor, ANCHOR_STATE_WORKING))
            if anchor.state == ANCHOR_STATE_WORKING:
                self.plan.add_job(PopQueueJob(anchor, 1))


class AnchorJob(Job):
    """job с передачей анкора"""

    def __init__(self, anchor, *args, **kwargs):
        self.anchor = anchor
        super().__init__(*args, **kwargs)


class ConfigureAnchorJob(AnchorJob):
    """Конфигурация анкора по дефолтному конфигу"""

    async def work(self):
        default_db_config = await db_objects.execute(
                DefaultConfigModel.select()
                .where(DefaultConfigModel.active == 1)
                .order_by(DefaultConfigModel.id.desc()))
        default_db_config = default_db_config[0]
        anchor_config = AnchorConfigurationFrame()
        anchor_config.chan = default_db_config.chan
        anchor_config.prf = default_db_config.prf
        anchor_config.txPreambLength = default_db_config.txPreambLength
        anchor_config.rxPAC = default_db_config.rxPAC
        anchor_config.txCode = default_db_config.txCode
        anchor_config.rxCode = default_db_config.rxCode
        anchor_config.nsSFD = default_db_config.nsSFD
        anchor_config.dataRate = default_db_config.dataRate
        anchor_config.phrMode = default_db_config.phrMode
        anchor_config.sfdTO = default_db_config.sfdTO
        anchor_config.my_master_ID = default_db_config.my_master_ID
        anchor_config.role = default_db_config.role
        anchor_config.master_period = default_db_config.master_period
        anchor_config.submaster_delay = default_db_config.submaster_delay
        response = await set_config(self.anchor.ip_address, anchor_config.to_binary())
        print('Set config result : %s\n%r\n' % (response.code, response.payload))
        self.anchor.config = anchor_config.to_json()
        await db_objects.update(self.anchor)
        self.plan.add_job(SetStateAnchorJob(self.anchor, ANCHOR_STATE_CONFIGURED))


class SetStateAnchorJob(AnchorJob):
    """Установка анкора в рабочий режим"""

    def __init__(self, anchor, state, *args, **kwargs):
        self.state = state
        super().__init__(anchor, *args, **kwargs)

    async def work(self):
        response = await set_state(self.anchor.ip_address,
                                   AnchorStateFrame(bytes([self.state])).to_binary())
        print('Set state result : %s\n%r\n' % (response.code, response.payload))
        self.anchor.state = self.state
        await db_objects.update(self.anchor)
        if self.state == ANCHOR_STATE_CONFIGURED:
            self.plan.add_job(SetStateAnchorJob(self.anchor, ANCHOR_STATE_WORKING))
        if self.state == ANCHOR_STATE_WORKING:
            self.plan.add_job(PopQueueJob(self.anchor, 5))


class PopQueueJob(RegularJob, AnchorJob):
    """Регулярный опрос анкора"""

    async def work(self):
        response = await popqueue(self.anchor.ip_address)
        print('Popqueue result: %s\n%r' % (response.code, response.payload))
        if response.payload[0] == 48:  # 0x30
            frame = CPPTXFrame(response.payload)
        if response.payload[0] == 49:  # 0x31
            frame = CPPRXFrame(response.payload)
        if response.payload[0] == 50:  # 0x32
            frame = BlinkFrame(response.payload)

        report = await db_objects.create(AnchorReportModel,
                                         anchor=self.anchor, record=frame.to_json())

        # include solver
        solved_data = solve(frame)

        data = json.loads(frame.to_json())
        data["anchor_id"] = self.anchor.id
        data["solver"] = solved_data

        # publish to rabbitmq
        rabbit_publish(json.dumps(data))
        # publish to influxdb
        influx_publish(data)

        # print(data)


# "{\"parameter\": \"value\"}"
class EmptyJob(Job):
    async def work(self):
        print("Empty work processed!")
        print(self.parameters)


class EmptyAnchorJob(AnchorJob):
    async def work(self):
        print("Empty anchor work processed!")
        print(self.anchor.ip_address)
        print(self.parameters)


class RemoteJob(RegularJob):
    """Смотрим не появились ли новые задачи из внешних источников"""

    async def work(self):
        job_list = await db_objects.execute(JobModel.select())
        for job in job_list:
            job_class = job.name
            try:
                module_path, class_name = "execplan", job_class
                module = import_module(module_path)
                job_class = getattr(module, class_name)
            except (ImportError, AttributeError) as e:
                raise ImportError(job_class)

            parameters = {}
            if job.parameters:
                parameters = json.loads(job.parameters)
            if job.anchor_ids:
                for anchor_id in job.anchor_ids.split(","):
                    anchor = await db_objects.get(AnchorModel, id=anchor_id)
                    self.plan.add_job(job_class(anchor=anchor, parameters=parameters))
            else:
                self.plan.add_job(job_class(parameters=parameters))

            await db_objects.delete(job)


class ExecutionPlan:
    """
    Очередь задач (джобов) с системной частой пробегает по всем джобам
    тех кому подошла очередь выполняться выполняет
    """
    queue = deque()

    def __init__(self):
        Job.set_plan(self)

    def add_job(self, job):
        self.queue.append(job)

    async def process(self):
        if self.queue:
            count = len(self.queue)
            for i in range(count):
                await self._process_job()

    async def _process_job(self):
        job = self.queue.popleft()
        if job.its_time():
            await job.work()

        if job.need_continue():
            self.queue.append(job)


execution_plan = ExecutionPlan()
execution_plan.add_job(InitAnchors())
execution_plan.add_job(RemoteJob(3))
