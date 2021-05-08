
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, BIGINT, VARCHAR, ForeignKey, JSON
from sqlalchemy.orm import relation
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True

    id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)

    def __repr__(self):
        return "<{0.__class__.__name__}(id={0.id!r})>".format(self)


class DefaultConfigModel(BaseModel):
    __tablename__ = 'default_config'

    name = Column(VARCHAR(255), nullable=False)
    active = Column(BIGINT(), default=True)
    chan = Column(BIGINT(), default=0)
    prf = Column(BIGINT(), default=0)
    txPreambLength = Column(BIGINT(), default=0)
    rxPAC = Column(BIGINT(), default=0)
    txCode = Column(BIGINT(), default=0)
    rxCode = Column(BIGINT(), default=0)
    nsSFD = Column(BIGINT(), default=0)
    dataRate = Column(BIGINT(), default=0)
    phrMode = Column(BIGINT(), default=0)
    sfdTO = Column(BIGINT(), default=0)
    my_master_ID = Column(BIGINT(), default=0)
    role = Column(BIGINT(), default=0)
    master_period = Column(BIGINT(), default=0)
    submaster_delay = Column(BIGINT(), default=0)


class AnchorModel(BaseModel):
    __tablename__ = 'anchors'

    ip_address = Column(VARCHAR(255), nullable=False)
    state = Column(Integer(), default=True)
    config = Column(JSON(), nullable=True)


class AnchorReportModel(BaseModel):
    __tablename__ = 'anchor_reports'

    anchor = Column(ForeignKey('anchors.id', ondelete='CASCADE'), nullable=False, index=True)
    record = Column(JSON())


class JobModel(BaseModel):
    __tablename__ = 'jobs'

    name = Column(VARCHAR(255), nullable=False)
    anchor_ids = Column(VARCHAR(255), nullable=True)
    parameters = Column(JSON(), nullable=True)


engine = create_async_engine(
    "postgresql+asyncpg://postgres:postgres@localhost:5435/postgres",
    echo=True,
)


async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
