from datetime import date, datetime, timezone
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.currency import CurrencyRate
from app.models.exchange_rate import ExchangeRate


def save_rates(db: Session, data: ExchangeRate) -> CurrencyRate:
    """Save or update exchange rates (upsert)."""
    rate_date = date.fromisoformat(data.date)
    existing = (
        db.query(CurrencyRate)
        .filter(
            CurrencyRate.bank_name == data.bank,
            CurrencyRate.date == rate_date,
        )
        .first()
    )

    if existing:
        existing.rates = data.model_dump()["rates"]
        existing.timestamp = datetime.now(timezone.utc)
    else:
        existing = CurrencyRate(
            bank_name=data.bank,
            date=rate_date,
            rates=data.model_dump()["rates"],
        )
        db.add(existing)

    db.commit()
    db.refresh(existing)
    return existing


def get_all_rates(
    db: Session, skip: int = 0, limit: int = 100
) -> List[CurrencyRate]:
    return (
        db.query(CurrencyRate)
        .order_by(CurrencyRate.timestamp.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_rates_by_bank(
    db: Session, bank_name: str, skip: int = 0, limit: int = 100
) -> List[CurrencyRate]:
    return (
        db.query(CurrencyRate)
        .filter(CurrencyRate.bank_name == bank_name)
        .order_by(CurrencyRate.timestamp.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_rates_by_date(
    db: Session, target_date: date, skip: int = 0, limit: int = 100
) -> List[CurrencyRate]:
    return (
        db.query(CurrencyRate)
        .filter(CurrencyRate.date == target_date)
        .order_by(CurrencyRate.timestamp.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_rates_by_bank_and_date(
    db: Session, bank_name: str, target_date: date
) -> Optional[CurrencyRate]:
    return (
        db.query(CurrencyRate)
        .filter(
            CurrencyRate.bank_name == bank_name,
            CurrencyRate.date == target_date,
        )
        .first()
    )


def get_latest_rates(db: Session) -> List[CurrencyRate]:
    subq = (
        db.query(
            CurrencyRate.bank_name,
            func.max(CurrencyRate.timestamp).label("max_ts"),
        )
        .group_by(CurrencyRate.bank_name)
        .subquery()
    )

    return (
        db.query(CurrencyRate)
        .join(
            subq,
            (CurrencyRate.bank_name == subq.c.bank_name)
            & (CurrencyRate.timestamp == subq.c.max_ts),
        )
        .all()
    )
