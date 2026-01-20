from typing import Dict, Optional

from pydantic import BaseModel


class Rate(BaseModel):
    buy: Optional[float] = None
    sell: Optional[float] = None


class CurrencyDetail(BaseModel):
    cash: Rate
    noncash: Rate


class ExchangeRate(BaseModel):
    date: str
    bank: str
    rates: Dict[str, CurrencyDetail]
