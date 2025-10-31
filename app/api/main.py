"""
Монгол банкны валютын ханшийн FastAPI апликейшн.
"""

import datetime
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import repository
from app.db.database import get_db, init_db
from app.services.scraper_service import ScraperService

app = FastAPI(
    title="Mongolian Bank Exchange Rates API",
    description="API for fetching exchange rates from Mongolian banks",
    version="1.0.0",
)


class CurrencyRateResponse(BaseModel):
    """Валютын ханшийн хариу загвар."""

    id: int
    bank_name: str
    date: datetime.date
    rates: dict
    timestamp: datetime.datetime

    class Config:
        from_attributes = True


@app.on_event("startup")
def on_startup():
    """Апликейшн эхлэхэд өгөгдлийн санг эхлүүлэх."""
    init_db()


@app.get("/", tags=["Root"])
def root():
    """Үндсэн эндпойнт - API-ийн мэдээлэл."""
    return {
        "message": "Mongolian Bank Exchange Rates API",
        "version": "1.0.0",
        "endpoints": {
            "/rates": "Get all rates from database",
            "/rates/latest": "Get latest rates for all banks",
            "/rates/bank/{bank_name}": "Get rates for specific bank from database",
            "/rates/date/{date}": "Get rates for specific date from database",
            "/rates/bank/{bank_name}/date/{date}": "Get rate for specific bank and date",
            "/scrape/all": "Scrape all banks and return fresh data",
            "/scrape/bank/{bank_name}": "Scrape specific bank and return fresh data",
        },
    }


@app.get("/rates", response_model=List[CurrencyRateResponse], tags=["Database"])
def get_all_rates(
    skip: int = Query(0, ge=0, description="Алгасах бичлэгийн тоо"),
    limit: int = Query(100, ge=1, le=1000, description="Буцаах бичлэгийн дээд хязгаар"),
    db: Session = Depends(get_db),
):
    """
    Өгөгдлийн сангаас бүх валютын ханшийг хуудаслалттайгаар авах.

    - **skip**: Алгасах бичлэгийн тоо (хуудаслалтад)
    - **limit**: Буцаах бичлэгийн дээд хязгаар (хамгийн ихдээ 1000)
    """
    rates = repository.get_all_rates(db, skip=skip, limit=limit)
    return rates


@app.get("/rates/latest", response_model=List[CurrencyRateResponse], tags=["Database"])
def get_latest_rates(db: Session = Depends(get_db)):
    """
    Бүх банкны хамгийн сүүлийн валютын ханшийг авах.
    Банк бүрийн хамгийн сүүлийн ханшийг буцаана.
    """
    rates = repository.get_latest_rates(db)
    return rates


@app.get("/rates/bank/{bank_name}", response_model=List[CurrencyRateResponse], tags=["Database"])
def get_rates_by_bank(
    bank_name: str,
    skip: int = Query(0, ge=0, description="Алгасах бичлэгийн тоо"),
    limit: int = Query(100, ge=1, le=1000, description="Буцаах бичлэгийн дээд хязгаар"),
    db: Session = Depends(get_db),
):
    """
    Өгөгдлийн сангаас тодорхой банкны валютын ханшийг авах.

    - **bank_name**: Банкны нэр (ж: KhanBank, GolomtBank, ArigBank)
    - **skip**: Алгасах бичлэгийн тоо (хуудаслалтад)
    - **limit**: Буцаах бичлэгийн дээд хязгаар (хамгийн ихдээ 1000)
    """
    rates = repository.get_rates_by_bank(db, bank_name, skip=skip, limit=limit)
    if not rates:
        raise HTTPException(status_code=404, detail=f"No rates found for bank: {bank_name}")
    return rates


@app.get("/rates/date/{date}", response_model=List[CurrencyRateResponse], tags=["Database"])
def get_rates_by_date(
    date: str,
    skip: int = Query(0, ge=0, description="Алгасах бичлэгийн тоо"),
    limit: int = Query(100, ge=1, le=1000, description="Буцаах бичлэгийн дээд хязгаар"),
    db: Session = Depends(get_db),
):
    """
    Өгөгдлийн сангаас тодорхой өдрийн валютын ханшийг авах.

    - **date**: Огноо YYYY-MM-DD форматаар
    - **skip**: Алгасах бичлэгийн тоо (хуудаслалтад)
    - **limit**: Буцаах бичлэгийн дээд хязгаар (хамгийн ихдээ 1000)
    """
    try:
        date_obj = datetime.date.fromisoformat(date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    rates = repository.get_rates_by_date(db, date_obj, skip=skip, limit=limit)
    if not rates:
        raise HTTPException(status_code=404, detail=f"No rates found for date: {date}")
    return rates


@app.get("/rates/bank/{bank_name}/date/{date}", response_model=CurrencyRateResponse, tags=["Database"])
def get_rate_by_bank_and_date(bank_name: str, date: str, db: Session = Depends(get_db)):
    """
    Өгөгдлийн сангаас тодорхой банк болон огнооны валютын ханшийг авах.

    - **bank_name**: Банкны нэр (ж: KhanBank, GolomtBank, ArigBank)
    - **date**: Огноо YYYY-MM-DD форматаар
    """
    try:
        date_obj = datetime.date.fromisoformat(date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    rate = repository.get_rates_by_bank_and_date(db, bank_name, date_obj)
    if not rate:
        raise HTTPException(status_code=404, detail=f"No rate found for bank: {bank_name} on date: {date}")
    return rate


@app.post("/scrape/all", tags=["Scraping"])
def scrape_all_banks(date: Optional[str] = Query(None, description="Огноо YYYY-MM-DD форматаар (өнөөдөр байна)")):
    """
    Бүх банкнаас валютын ханшийг татаж өгөгдлийн санд хадгалах.
    Татах үйлдлийн хураангуйг буцаана.

    - **date**: Сонголттой огноо параметр (өнөөдөр байна)
    """
    scraper = ScraperService(date=date)
    scraper.run_crawlers()
    return {"message": "Scraping completed", "date": scraper.date, "status": "success"}


@app.get("/scrape/bank/{bank_name}", tags=["Scraping"])
def scrape_bank(
    bank_name: str, date: Optional[str] = Query(None, description="Огноо YYYY-MM-DD форматаар (өнөөдөр байна)")
):
    """
    Тодорхой банкнаас валютын ханшийг татаж шинэ өгөгдлийг буцаах.
    Өгөгдлийн санд хадгалахгүй - шууд мэдээлэл буцаана.

    Дэмжигдсэн банкууд:
    - KhanBank
    - GolomtBank, Golomt
    - MongolBank
    - TDBM
    - XacBank
    - ArigBank
    - BogdBank
    - StateBank
    - CapitronBank
    - TransBank
    - NIBank
    - MBank
    - CKBank

    - **bank_name**: Татах банкны нэр
    - **date**: Сонголттой огноо параметр (өнөөдөр байна)
    """
    scraper = ScraperService(date=date)
    rates = scraper.scrape_bank(bank_name)

    if rates is None:
        raise HTTPException(
            status_code=404,
            detail=f"Bank not found: {bank_name}. Check /scrape/bank/{{bank_name}} endpoint description for supported banks.",
        )

    return {"bank": bank_name, "date": scraper.date, "rates": rates}
