import datetime

from sqlalchemy import JSON, Column, Date, DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class CurrencyRate(Base):
    __tablename__ = "currency_rates"

    id = Column(Integer, primary_key=True, index=True)
    bank_name = Column(String, index=True)
    date = Column(Date, index=True)
    rates = Column(JSON)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
