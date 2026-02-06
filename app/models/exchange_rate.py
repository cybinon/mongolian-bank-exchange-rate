import datetime
from typing import Dict, Optional

from pydantic import BaseModel, Field


class Rate(BaseModel):
    buy: Optional[float] = Field(
        default=None,
        description="Авах ханш",
        examples=[3430.5],
    )
    sell: Optional[float] = Field(
        default=None,
        description="Зарах ханш",
        examples=[3450.0],
    )


class CurrencyDetail(BaseModel):
    cash: Rate = Field(
        default_factory=Rate,
        description="Бэлэн ханш",
        examples=[{"buy": 3430.5, "sell": 3450.0}],
    )
    noncash: Rate = Field(
        default_factory=Rate,
        description="Бэлэн бус ханш",
        examples=[{"buy": 3435.0, "sell": 3445.0}],
    )


class ExchangeRate(BaseModel):
    date: str = Field(
        description="Өдрийн ханш (YYYY-MM-DD)",
        examples=["2024-01-15"],
    )
    bank: str = Field(
        description="Банкны нэр",
        examples=["KhanBank"],
    )
    rates: Dict[str, CurrencyDetail] = Field(
        description="Валютын кодоор ангилагдсан ханш",
        examples=[
            {
                "usd": {
                    "cash": {"buy": 3430.5, "sell": 3450.0},
                    "noncash": {"buy": 3435.0, "sell": 3445.0},
                }
            }
        ],
    )


class CurrencyRateResponse(BaseModel):
    id: int = Field(
        description="Ханшийн Id",
        examples=[1],
    )
    bank_name: str = Field(
        description="Банкны нэр",
        examples=["KhanBank"],
    )
    date: datetime.date = Field(
        description="Өдрийн ханш (YYYY-MM-DD)",
        examples=["2024-01-15"],
    )
    rates: Dict[str, CurrencyDetail] = Field(
        description="Валютын кодоор ангилагдсан ханш",
        examples=[
            {
                "usd": {
                    "cash": {"buy": 3430.5, "sell": 3450.0},
                    "noncash": {"buy": 3435.0, "sell": 3445.0},
                }
            }
        ],
    )
    timestamp: datetime.datetime = Field(
        description="Хэзээ ханш бүртгэгдсэн",
        examples=["2024-01-15T10:30:00Z"],
    )

    model_config = {"from_attributes": True}
