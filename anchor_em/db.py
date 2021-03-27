import asyncio
import functools
import json

import peewee_async

from peewee import Model, CharField, ForeignKeyField, BigIntegerField, BooleanField, IntegerField
from playhouse.postgres_ext import *


my_json_dumps = functools.partial(json.dumps, ensure_ascii=False)
database = peewee_async.PostgresqlDatabase(
    database="postgres",
    user="postgres",
    password="postgres",
    host="db",
    port=5432
)


class BaseModel(Model):
    class Meta:
        database = database


class DefaultConfigModel(BaseModel):
    name = CharField()
    active = BooleanField(default=True)
    chan = BigIntegerField()
    prf = BigIntegerField()
    txPreambLength = BigIntegerField()
    rxPAC = BigIntegerField()
    txCode = BigIntegerField()
    rxCode = BigIntegerField()
    nsSFD = BigIntegerField()
    dataRate = BigIntegerField()
    phrMode = BigIntegerField()
    sfdTO = BigIntegerField()
    my_master_ID = BigIntegerField()
    role = BigIntegerField()
    master_period = BigIntegerField()
    submaster_delay = BigIntegerField()

    class Meta:
        order_by = ['-id']


class AnchorModel(BaseModel):
    ip_address = CharField()
    state = IntegerField(default=0)
    config = JSONField(null=True)


class AnchorReportModel(BaseModel):
    anchor = ForeignKeyField(AnchorModel, backref="reports")
    record = JSONField(null=True)


class JobModel(BaseModel):
    name = CharField()
    anchor_ids = CharField(null=True)
    parameters = JSONField(null=True)


def create_tables():
    # sync code!
    DefaultConfigModel.create_table(True)
    AnchorModel.create_table(True)
    AnchorReportModel.create_table(True)
    JobModel.create_table(True)
    database.close()


def create_default_config():
    config = DefaultConfigModel(
        name="DefaultConfig",
        chan=0,
        prf=1,
        txPreambLength=24,
        rxPAC=3,
        txCode=8,
        rxCode=8,
        nsSFD=0,
        dataRate=2,
        phrMode=3,
        sfdTO=1058,
        my_master_ID=66666655198446,
        role=1,
        master_period=7777,
        submaster_delay=253,
    )
    config.save()


# Create async models manager:
objects = peewee_async.Manager(database)

# db creation, sync code for proper order
create_tables()
# create_default_config()


# No need for sync anymore! sync code doesn't working
database.set_allow_sync(False)
