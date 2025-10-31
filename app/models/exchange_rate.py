"""
Pydantic models for exchange rates.
"""

from typing import Dict, Optional

from pydantic import BaseModel


class Rate(BaseModel):
    """Buy and sell rates model."""

    buy: Optional[float] = None
    sell: Optional[float] = None


class CurrencyDetail(BaseModel):
    """Detailed cash and non-cash rates."""

    cash: Rate
    noncash: Rate


class ExchangeRate(BaseModel):
    """Base model representing a bank's exchange rates."""

    date: str
    bank: str
    rates: Dict[str, CurrencyDetail]
