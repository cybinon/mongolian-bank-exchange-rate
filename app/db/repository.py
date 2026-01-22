import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.currency import CurrencyRate
from app.models.exchange_rate import ExchangeRate
from app.utils.logger import get_logger

logger = get_logger("db")


def save_rates(db: Session, rate_data: ExchangeRate):
    try:
        db_rate = CurrencyRate(
            bank_name=rate_data.bank, date=datetime.date.fromisoformat(rate_data.date), rates=rate_data.dict()["rates"]
        )
        db.add(db_rate)
        db.commit()
        db.refresh(db_rate)
        return db_rate
    except Exception as e:
        db.rollback()
        logger.exception(f"Failed to save rates for {rate_data.bank}: {e}")
        raise


def get_all_rates(db: Session, skip: int = 0, limit: int = 100) -> List[CurrencyRate]:
    return db.query(CurrencyRate).order_by(CurrencyRate.timestamp.desc()).offset(skip).limit(limit).all()


def get_rates_by_bank(db: Session, bank_name: str, skip: int = 0, limit: int = 100) -> List[CurrencyRate]:
    return (
        db.query(CurrencyRate)
        .filter(CurrencyRate.bank_name == bank_name)
        .order_by(CurrencyRate.timestamp.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_rates_by_date(db: Session, date: datetime.date, skip: int = 0, limit: int = 100) -> List[CurrencyRate]:
    return (
        db.query(CurrencyRate)
        .filter(CurrencyRate.date == date)
        .order_by(CurrencyRate.timestamp.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_rates_by_bank_and_date(db: Session, bank_name: str, date: datetime.date) -> Optional[CurrencyRate]:
    return (
        db.query(CurrencyRate)
        .filter(CurrencyRate.bank_name == bank_name, CurrencyRate.date == date)
        .order_by(CurrencyRate.timestamp.desc())
        .first()
    )


def get_latest_rates(db: Session) -> List[CurrencyRate]:
    from sqlalchemy import func

    subquery = (
        db.query(CurrencyRate.bank_name, func.max(CurrencyRate.timestamp).label("max_ts"))
        .group_by(CurrencyRate.bank_name)
        .subquery()
    )
    return (
        db.query(CurrencyRate)
        .join(
            subquery, (CurrencyRate.bank_name == subquery.c.bank_name) & (CurrencyRate.timestamp == subquery.c.max_ts)
        )
        .all()
    )
