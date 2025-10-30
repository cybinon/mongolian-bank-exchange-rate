"""
Валютын ханшийн өгөгдлийн сангийн үйлдлүүдийн репозитори модуль.
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
    Ханшийг өгөгдлийн санд хадгалах.
    
    Args:
        db: Өгөгдлийн сангийн сешн
        rate_data: Хадгалах ханш агуулсан ExchangeRate объект
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
        logger.info(f"{rate_data.bank}-ны {rate_data.date} өдрийн ханшийг хадгаллаа")
        return db_rate
    except Exception as e:
        db.rollback()
        logger.error(f"{rate_data.bank}-ны ханш хадгалахад алдаа гарлаа: {e}")
        raise


def get_all_rates(db: Session, skip: int = 0, limit: int = 100) -> List[CurrencyRate]:
    """
    Бүх валютын ханшийг хуудаслалттайгаар авах.
    
    Args:
        db: Өгөгдлийн сангийн сешн
        skip: Алгасах бичлэгийн тоо
        limit: Буцаах хамгийн их бичлэгийн тоо
        
    Returns:
        CurrencyRate объектуудын жагсаалт
    """
    return db.query(CurrencyRate).order_by(CurrencyRate.timestamp.desc()).offset(skip).limit(limit).all()


def get_rates_by_bank(db: Session, bank_name: str, skip: int = 0, limit: int = 100) -> List[CurrencyRate]:
    """
    Тодорхой банкны валютын ханшийг авах.
    
    Args:
        db: Өгөгдлийн сангийн сешн
        bank_name: Банкны нэр
        skip: Алгасах бичлэгийн тоо
        limit: Буцаах хамгийн их бичлэгийн тоо
        
    Returns:
        Заасан банкны CurrencyRate объектуудын жагсаалт
    """
    return db.query(CurrencyRate).filter(
        CurrencyRate.bank_name == bank_name
    ).order_by(CurrencyRate.timestamp.desc()).offset(skip).limit(limit).all()


def get_rates_by_date(db: Session, date: datetime.date, skip: int = 0, limit: int = 100) -> List[CurrencyRate]:
    """
    Тодорхой өдрийн валютын ханшийг авах.
    
    Args:
        db: Өгөгдлийн сангийн сешн
        date: Хайх огноо
        skip: Алгасах бичлэгийн тоо
        limit: Буцаах хамгийн их бичлэгийн тоо
        
    Returns:
        Заасан өдрийн CurrencyRate объектуудын жагсаалт
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
    Тодорхой банк болон огнооны валютын ханшийг авах.
    
    Args:
        db: Өгөгдлийн сангийн сешн
        bank_name: Банкны нэр
        date: Хайх огноо
        
    Returns:
        CurrencyRate объект эсвэл олдоогүй бол None
    """
    return db.query(CurrencyRate).filter(
        CurrencyRate.bank_name == bank_name,
        CurrencyRate.date == date
    ).order_by(CurrencyRate.timestamp.desc()).first()


def get_latest_rates(db: Session) -> List[CurrencyRate]:
    """
    Банк бүрийн хамгийн сүүлийн ханшийг авах.
    
    Args:
        db: Өгөгдлийн сангийн сешн
        
    Returns:
        Банк бүрийн хамгийн сүүлийн CurrencyRate объектуудын жагсаалт
    """
    # Бүх банкны нэрсийг авах
    banks = db.query(CurrencyRate.bank_name).distinct().all()
    
    latest_rates = []
    for (bank_name,) in banks:
        latest = db.query(CurrencyRate).filter(
            CurrencyRate.bank_name == bank_name
        ).order_by(CurrencyRate.timestamp.desc()).first()
        if latest:
            latest_rates.append(latest)
    
    return latest_rates

