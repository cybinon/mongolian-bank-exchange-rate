import datetime
from typing import Dict, Optional

from pydantic import BaseModel, Field


class Rate(BaseModel):
    buy: Optional[float] = Field(None, description="Авах ханш", examples=[3420.5])
    sell: Optional[float] = Field(None, description="Зарах ханш", examples=[3450.0])


class CurrencyDetail(BaseModel):
    cash: Rate = Field(..., description="Бэлэн мөнгөний ханш")
    noncash: Rate = Field(..., description="Бэлэн бус мөнгөний ханш")


class ExchangeRate(BaseModel):
    date: str
    bank: str
    rates: Dict[str, CurrencyDetail]


class CurrencyRateResponse(BaseModel):
    id: int = Field(..., description="Бичлэгийн ID", examples=[1])
    bank_name: str = Field(..., description="Банкны нэр", examples=["KhanBank"])
    date: datetime.date = Field(..., description="Ханшийн огноо", examples=["2026-01-22"])
    rates: Dict[str, CurrencyDetail] = Field(
        ...,
        description="Валютын ханшууд (USD, EUR, CNY, JPY, RUB, KRW, GBP гэх мэт)",
        examples=[
            {
                "usd": {"cash": {"buy": 3420.5, "sell": 3450.0}, "noncash": {"buy": 3415.0, "sell": 3455.0}},
                "eur": {"cash": {"buy": 3720.0, "sell": 3780.0}, "noncash": {"buy": 3715.0, "sell": 3785.0}},
            }
        ],
    )
    timestamp: datetime.datetime = Field(..., description="Бичлэг үүссэн цаг")

    class Config:
        from_attributes = True
