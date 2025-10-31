"""
Repository module for database operations on exchange rates.
"""
from sqlalchemy.orm import Session
from app.models.currency import CurrencyRate
from app.models.exchange_rate import ExchangeRate
from app.utils.logger import get_logger
import datetime
from typing import List, Optional

logger = get_logger(__name__)


def save_rates(db: Session, rate_data: ExchangeRate):
    """
    Save rates into the database.

    Args:
        db: SQLAlchemy session
        rate_data: ExchangeRate object to persist
    """
    try:
        db_rate = CurrencyRate(
            bank_name=rate_data.bank,
            date=datetime.date.fromisoformat(rate_data.date),
            rates=rate_data.dict()['rates']
        )
        db.add(db_rate)
        db.commit()
        db.refresh(db_rate)
        logger.info(f"Saved {rate_data.bank} rates for {rate_data.date}")
        return db_rate
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to save rates for {rate_data.bank}: {e}")
        raise


def get_all_rates(db: Session, skip: int = 0, limit: int = 100) -> List[CurrencyRate]:
    """
    Get all rates with pagination.

    Args:
        db: SQLAlchemy session
        skip: Number of rows to skip
        limit: Max number of rows to return

    Returns:
        List of CurrencyRate objects
    """
    return db.query(CurrencyRate).order_by(CurrencyRate.timestamp.desc()).offset(skip).limit(limit).all()


def get_rates_by_bank(db: Session, bank_name: str, skip: int = 0, limit: int = 100) -> List[CurrencyRate]:
    """
    Get rates for a specific bank.

    Args:
        db: SQLAlchemy session
        bank_name: Bank name
        skip: Number of rows to skip
        limit: Max number of rows to return

    Returns:
        List of CurrencyRate objects for the bank
    """
    return db.query(CurrencyRate).filter(
        CurrencyRate.bank_name == bank_name
    ).order_by(CurrencyRate.timestamp.desc()).offset(skip).limit(limit).all()


def get_rates_by_date(db: Session, date: datetime.date, skip: int = 0, limit: int = 100) -> List[CurrencyRate]:
    """
    Get rates for a specific date.

    Args:
        db: SQLAlchemy session
        date: Target date
        skip: Number of rows to skip
        limit: Max number of rows to return

    Returns:
        List of CurrencyRate objects for the date
    """
    return db.query(CurrencyRate).filter(
        CurrencyRate.date == date
    ).order_by(CurrencyRate.timestamp.desc()).offset(skip).limit(limit).all()


def get_rates_by_bank_and_date(
    db: Session, 
    bank_name: str, 
    date: datetime.date
) -> Optional[CurrencyRate]:
    """
    Get the rate for a specific bank and date.

    Args:
        db: SQLAlchemy session
        bank_name: Bank name
        date: Target date

    Returns:
        CurrencyRate object or None if not found
    """
    return db.query(CurrencyRate).filter(
        CurrencyRate.bank_name == bank_name,
        CurrencyRate.date == date
    ).order_by(CurrencyRate.timestamp.desc()).first()


def get_latest_rates(db: Session) -> List[CurrencyRate]:
    """
    Get the latest rate for each bank.

    Args:
        db: SQLAlchemy session

    Returns:
        List of the latest CurrencyRate per bank
    """
    # Distinct bank names
    banks = db.query(CurrencyRate.bank_name).distinct().all()
    
    latest_rates = []
    for (bank_name,) in banks:
        latest = db.query(CurrencyRate).filter(
            CurrencyRate.bank_name == bank_name
        ).order_by(CurrencyRate.timestamp.desc()).first()
        if latest:
            latest_rates.append(latest)
    
    return latest_rates

