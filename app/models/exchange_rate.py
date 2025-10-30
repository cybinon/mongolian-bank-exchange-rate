"""
Валютын ханшийн Pydantic загварууд.
"""
from pydantic import BaseModel
from typing import Dict, Optional

class Rate(BaseModel):
    """Худалдан авах болон худалдах ханшийн загвар."""
    buy: Optional[float] = None
    sell: Optional[float] = None

class CurrencyDetail(BaseModel):
    """Бэлэн болон бэлэн бус валютын ханшийн дэлгэрэнгүй загвар."""
    cash: Rate
    noncash: Rate

class ExchangeRate(BaseModel):
    """Банкны валютын ханшийн үндсэн загвар."""
    date: str
    bank: str
    rates: Dict[str, CurrencyDetail]
