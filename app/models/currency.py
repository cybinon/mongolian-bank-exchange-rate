from datetime import datetime, timezone

from sqlalchemy import JSON, Column, Date, DateTime, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


def utc_now():
    return datetime.now(timezone.utc)


class CurrencyRate(Base):
    __tablename__ = "currency_rates"

    id = Column(Integer, primary_key=True, index=True)
    bank_name = Column(String, index=True)
    date = Column(Date, index=True)
    rates = Column(JSON)
    timestamp = Column(DateTime, default=utc_now)
