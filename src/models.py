from sqlalchemy import BigInteger, Column, DateTime, Float, String
from sqlalchemy.dialects.postgresql import JSONB

from .db import Base


class DataLoad(Base):
    __tablename__ = "data_load"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    dataset = Column(String, index=True)
    time = Column(DateTime)
    props = Column(JSONB)


class TransformerBasic(Base):
    __tablename__ = "transformer_basic"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    time = Column(DateTime, unique=True)
    power = Column(Float)
