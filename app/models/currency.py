"""
Валютын ханшийн өгөгдлийн сангийн SQLAlchemy загвар.
"""
from sqlalchemy import Column, Integer, String, JSON, DateTime, Date
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class CurrencyRate(Base):
    """Өгөгдлийн сангийн валютын ханшийн хүснэгтийн загвар."""
    __tablename__ = "currency_rates"

    id = Column(Integer, primary_key=True, index=True)
    bank_name = Column(String, index=True)
    date = Column(Date, index=True)
    rates = Column(JSON)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

