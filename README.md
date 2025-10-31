# Монголын банкны валютын ханш API

13 банкны валютын ханшийг цуглуулагч. Үүнд дараах банкууд багтана :

- 🏛️ **arigbank** — Ариг банк  
- 🏛️ **bogdbank** — Богд банк  
- 🏛️ **capitronbank** — Капитрон банк  
- 🏛️ **ckbank** — Чингис хаан банк  
- 🏛️ **golomt** — Голомт банк  
- 🏛️ **khanbank** — Хаан банк  
- 🏛️ **mbank** — М банк  
- 🏛️ **mongolbank** — Монгол банк  
- 🏛️ **nibank** — Үндэсний хөрөнгө оруулалтын банк  
- 🏛️ **statebank** — Төрийн банк  
- 🏛️ **tdbm** — Худалдаа хөгжлийн банк  
- 🏛️ **transbank** — Транс банк  
- 🏛️ **xacbank** — Хас банк

## Хурдан эхлэх (Docker)

```powershell
git clone https://github.com/btseee/mongolian-bank-exchange-rate.git
cd mongolian-bank-exchange-rate
Copy-Item .env.example .env
docker-compose up -d
```

Нээх:

- API: <http://localhost:8000>
- Docs: <http://localhost:8000/docs>

## Source-оос ажиллуулах

```powershell
python -m venv venv
./venv/Scripts/Activate.ps1
pip install -r requirements.txt
playwright install chromium
python -c "from app.db.database import init_db; init_db()"
uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000
```

## Орчны хувьсагчид (гол)

- DATABASE_URL: Өгөгдлийн сангийн холбоос (ж: sqlite:///./exchange_rates.db)
- CRON_SCHEDULE: cron формат, анхдагч `0 1 * * *`
- SSL_VERIFY: True/False
- REQUEST_TIMEOUT: секунд
- PLAYWRIGHT_TIMEOUT: миллисекунд
- Банкны холбоосууд: KHANBANK_URI, GOLOMT_URI, TDBM_URI, XACBANK_URI, ARIGBANK_URI, …

Бүрэн жагсаалтыг `.env.example` файлаас харна уу.

## docker-compose дахь сервисүүд

- api: FastAPI сервер
- cron: Товлосон горимоор хусагч
- db: PostgreSQL (сонголттой, SQLite ашиглаж болно)

## Түгээмэл командууд

```powershell
# Scheduler-ийг нэг удаа ажиллуулах
python cron.py

# Тодорхой банкны crawler ажиллуулах (жишээ)
$env:PYTHONPATH='.'; python app/crawlers/khanbank.py
```

## Төслийн бүтэц (богино)

```text
app/
  api/           # FastAPI апп (API doc-ийг хэвээр хадгалсан)
  crawlers/      # Банк тус бүрийн crawler-ууд
  db/            # Өгөгдлийн сан ба репозитор
  models/        # Pydantic ба SQLAlchemy моделууд
  services/      # Scraper service
  utils/         # Логгер ба туслахууд
cron.py          # Scheduler-ийн эхлэл
Dockerfile
docker-compose.yml
```

## Лиценз

MIT — [LICENSE](LICENSE.md)-ийг харна уу.
