import datetime
from typing import List

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.__version__ import __author__, __donation__, __license__, __url__, __version__
from app.db import repository
from app.db.database import get_db, init_db
from app.models.exchange_rate import CurrencyRateResponse
from app.utils.logger import get_logger

logger = get_logger("api")

SUPPORTED_BANKS = [
    "ArigBank",
    "BogdBank",
    "CapitronBank",
    "CKBank",
    "GolomtBank",
    "KhanBank",
    "MBank",
    "MongolBank",
    "NIBank",
    "StateBank",
    "TDBM",
    "TransBank",
    "XacBank",
]

app = FastAPI(
    title="Монголын Банкуудын Валютын Ханш API",
    description="""Монголын 13 банкны валютын ханшийг авах нийтийн API.

## Онцлогууд
- 📊 Монголын 13 томоохон банкны валютын ханш
- 🔄 Өдөр бүр 09:00 цагт (UTC+8) шинэчлэгдэнэ
- 📅 Өмнөх өдрүүдийн ханшийг хайх боломжтой
- 🏦 Банкаар шүүж хайх

## Дэмжигдсэн Банкууд
- Ариг Банк, Богд Банк, Капитрон Банк, Чингис Хаан Банк, Голомт Банк
- Хаан Банк, М Банк, Монгол Банк, Үндэсний Хөрөнгө Оруулалтын Банк, Төрийн Банк
- Худалдаа Хөгжлийн Банк, Транс Банк, Хас Банк

## Хязгаарлалт
Энэ бол үнэгүй нийтийн API. Хүсэлтийн тоог хэт ихэсгэхгүй байхыг хүсье.
""",
    version=__version__,
    contact={"name": __author__, "url": __url__} if __author__ else None,
    license_info={"name": __license__, "url": "https://opensource.org/licenses/MIT"},
    openapi_tags=[
        {"name": "Мэдээлэл", "description": "API-ийн мэдээлэл болон эрүүл мэндийн шалгалт"},
        {"name": "Валютын Ханш", "description": "Валютын ханшийн мэдээлэл авах"},
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()
    logger.info(f"API started - version {__version__}")


@app.get("/", tags=["Мэдээлэл"])
def root():
    """API-ийн мэдээлэл болон боломжит эцсийн цэгүүд."""
    return {
        "name": "Монголын Банкуудын Валютын Ханш API",
        "version": __version__,
        "description": "Монголын 13 банкны валютын ханшийг авах нийтийн API",
        "documentation": "/docs",
        "github": __url__,
        "donation": __donation__,
        "data_update": "Өдөр бүр 09:00 цагт (UTC+8)",
        "supported_banks": SUPPORTED_BANKS,
        "endpoints": {
            "/rates": "Бүх ханшийг авах (хуудаслалттай)",
            "/rates/latest": "Бүх банкны хамгийн сүүлийн ханш",
            "/rates/bank/{bank_name}": "Тодорхой банкны ханш",
            "/rates/date/{date}": "Тодорхой өдрийн ханш (YYYY-MM-DD)",
            "/rates/bank/{bank_name}/date/{date}": "Тодорхой банк, өдрийн ханш",
            "/health": "Эрүүл мэндийн шалгалт",
        },
    }


@app.get("/health", tags=["Мэдээлэл"])
def health_check():
    """Эрүүл мэндийн шалгалтын эцсийн цэг."""
    return {"status": "healthy", "version": __version__}


@app.get("/rates", response_model=List[CurrencyRateResponse], tags=["Валютын Ханш"])
def get_all_rates(
    skip: int = Query(0, ge=0, description="Алгасах бичлэгийн тоо"),
    limit: int = Query(100, ge=1, le=1000, description="Буцаах бичлэгийн дээд хязгаар"),
    db: Session = Depends(get_db),
):
    """
    Бүх валютын ханшийг хуудаслалттай авах.

    - **skip**: Алгасах бичлэгийн тоо (хуудаслалтад)
    - **limit**: Буцаах бичлэгийн дээд хязгаар (хамгийн ихдээ 1000)
    """
    rates = repository.get_all_rates(db, skip=skip, limit=limit)
    return rates


@app.get("/rates/latest", response_model=List[CurrencyRateResponse], tags=["Валютын Ханш"])
def get_latest_rates(db: Session = Depends(get_db)):
    """
    Бүх банкны хамгийн сүүлийн валютын ханшийг авах.

    Банк бүрийн хамгийн сүүлийн бичлэгийг буцаана.
    """
    rates = repository.get_latest_rates(db)
    return rates


@app.get("/rates/bank/{bank_name}", response_model=List[CurrencyRateResponse], tags=["Валютын Ханш"])
def get_rates_by_bank(
    bank_name: str,
    skip: int = Query(0, ge=0, description="Алгасах бичлэгийн тоо"),
    limit: int = Query(100, ge=1, le=1000, description="Буцаах бичлэгийн дээд хязгаар"),
    db: Session = Depends(get_db),
):
    """
    Тодорхой банкны валютын ханшийг авах.

    - **bank_name**: Банкны нэр (жишээ нь: KhanBank, GolomtBank, ArigBank)
    - **skip**: Алгасах бичлэгийн тоо (хуудаслалтад)
    - **limit**: Буцаах бичлэгийн дээд хязгаар (хамгийн ихдээ 1000)
    """
    rates = repository.get_rates_by_bank(db, bank_name, skip=skip, limit=limit)
    if not rates:
        raise HTTPException(status_code=404, detail=f"'{bank_name}' банкны ханш олдсонгүй")
    return rates


@app.get("/rates/date/{date}", response_model=List[CurrencyRateResponse], tags=["Валютын Ханш"])
def get_rates_by_date(
    date: str,
    skip: int = Query(0, ge=0, description="Алгасах бичлэгийн тоо"),
    limit: int = Query(100, ge=1, le=1000, description="Буцаах бичлэгийн дээд хязгаар"),
    db: Session = Depends(get_db),
):
    """
    Тодорхой өдрийн валютын ханшийг авах.

    - **date**: Огноо YYYY-MM-DD форматаар
    - **skip**: Алгасах бичлэгийн тоо (хуудаслалтад)
    - **limit**: Буцаах бичлэгийн дээд хязгаар (хамгийн ихдээ 1000)
    """
    try:
        date_obj = datetime.date.fromisoformat(date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Огнооны формат буруу. YYYY-MM-DD ашиглана уу")

    rates = repository.get_rates_by_date(db, date_obj, skip=skip, limit=limit)
    if not rates:
        raise HTTPException(status_code=404, detail=f"'{date}' өдрийн ханш олдсонгүй")
    return rates


@app.get("/rates/bank/{bank_name}/date/{date}", response_model=CurrencyRateResponse, tags=["Валютын Ханш"])
def get_rate_by_bank_and_date(bank_name: str, date: str, db: Session = Depends(get_db)):
    """
    Тодорхой банк, өдрийн валютын ханшийг авах.

    - **bank_name**: Банкны нэр (жишээ нь: KhanBank, GolomtBank, ArigBank)
    - **date**: Огноо YYYY-MM-DD форматаар
    """
    try:
        date_obj = datetime.date.fromisoformat(date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Огнооны формат буруу. YYYY-MM-DD ашиглана уу")

    rate = repository.get_rates_by_bank_and_date(db, bank_name, date_obj)
    if not rate:
        raise HTTPException(status_code=404, detail=f"'{bank_name}' банкны '{date}' өдрийн ханш олдсонгүй")
    return rate
