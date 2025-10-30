# Монгол Банкны Ханшийн Мэдээлэл Цуглуулагч

Монгол Улсын 13 томоохон банкны валютын ханшийг цуглуулж, олон нийтэд API-аар үзүүлдэг иж бүрэн систем. FastAPI, SQLAlchemy, Playwright технологи дээр бүтээгдсэн.

## 🏦 Дэмжигдсэн Банкууд

- **Хаан банк** - API-д суурилсан
- **Голомт банк** - API-д суурилсан
- **Худалдаа Хөгжлийн банк (ХХБ)** - Вэб скрэйпинг
- **Хас банк** - API-д суурилсан
- **Ариг банк** - Bearer token нэвтрэлт бүхий API
- **Богд банк** - Вэб скрэйпинг
- **Төрийн банк** - API-д суурилсан
- **Монгол банк** - API-д суурилсан
- **Капитрон банк** - API-д суурилсан
- **Транс банк** - Next.js өгөгдөл задлах
- **Үндэсний хөрөнгө оруулалтын банк (ҮХОБ)** - Вэб скрэйпинг
- **М-банк** - Вэб скрэйпинг
- **CK банк** - Playwright скрэйпинг

## 📋 Шаардлагатай зүйлс

- Python 3.8+
- pip
- Virtual environment (зөвлөмж)

## 🔧 Суулгах заавар

### 🐳 Docker-оор (Зөвлөмж)

Хамгийн хялбар арга - Docker ашиглах:

```bash
# 1. Repository-г татах
git clone https://github.com/btseee/mongolian-bank-exchange-rate.git
cd mongolian-bank-exchange-rate

# 2. .env файл үүсгэх
cp .env.example .env

# 3. Docker Compose-оор эхлүүлэх
docker-compose up -d

# 4. API шалгах
curl http://localhost:8000
# Эсвэл хөтөч нээж: http://localhost:8000/docs
```

**Дэлгэрэнгүй Docker заавар:** [DOCKER.md](DOCKER.md) харна уу.

### 🐍 Хурдан эхлүүлэх (Quick Start)

```bash
# 1. Репозиторийг татах
git clone https://github.com/btseee/mongolian-bank-exchange-rate.git
cd mongolian-bank-exchange-rate

# 2. Виртуал орчин үүсгэх
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Хамаарлуудыг суулгах
pip install -r requirements.txt

# 4. Playwright хөтчүүдийг суулгах (вэб скрэйпинг хийхэд шаардлагатай)
playwright install chromium

# 5. .env файл үүсгэх (жишээг доороос хар)
cp .env.example .env  # эсвэл гараар үүсгэ

# 6. Өгөгдлийн санг эхлүүлэх
python -c "from app.db.database import init_db; init_db()"

# 7. API серверийг ажиллуулах
uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000

# 8. Хөтөч нээж http://localhost:8000/docs руу орно
```

### Дэлгэрэнгүй заавар

#### 1. Репозиторийг татах

```bash
git clone https://github.com/btseee/mongolian-bank-exchange-rate.git
cd mongolian-bank-exchange-rate
```

#### 2. Виртуал орчин үүсгэх

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

#### 3. Хамаарлуудыг суулгах

```bash
pip install -r requirements.txt
```

#### 4. Playwright хөтчүүдийг суулгах

Зарим банкуудад вэб скрэйпинг шаардлагатай:

```bash
playwright install chromium
```

#### 5. Орчны хувьсагчдыг тохируулах

`.env` файл үүсгээд дараах тохиргоог оруулна уу:

```bash
# Өгөгдлийн сангийн тохиргоо
# SQLite жишээ (үндсэн)
DATABASE_URL=sqlite:///./exchange_rates.db

# PostgreSQL жишээ
# DATABASE_URL=postgresql://user:password@localhost:5432/exchange_rates

# MySQL жишээ
# DATABASE_URL=mysql://user:password@localhost:3306/exchange_rates

# Хуваарийн тохиргоо (cron формат: минут цаг өдөр сар долоо хоног)
# Үндсэн: Өдөр бүр 01:00 цагт ажиллана
CRON_SCHEDULE=0 1 * * *

# SSL тохиргоо
SSL_VERIFY=False

# Хугацааны хязгаар (секунд)
REQUEST_TIMEOUT=30
PLAYWRIGHT_TIMEOUT=60000
```

#### 6. Өгөгдлийн санг эхлүүлэх

```bash
python -c "from app.db.database import init_db; init_db()"
```

Энэ нь `exchange_rates.db` файл үүсгэж, шаардлагатай хүснэгтүүдийг бүтээнэ.

## 🎯 Хэрэглэх заавар

### API серверийг ажиллуулах

FastAPI серверийг эхлүүлэх:

```bash
uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000
```

API дараах хаягуудаар ашиглах боломжтой:

- **API**: <http://localhost:8000>
- **Интерактив баримтжуулалт**: <http://localhost:8000/docs>
- **Өөр баримтжуулалт**: <http://localhost:8000/redoc>

### Хуваарийн цуглуулагчийг ажиллуулах

Хуваарьт цуглуулагчийг эхлүүлэх:

```bash
python cron.py
```

Энэ нь:

1. Эхлэхдээ шууд цуглуулалт хийнэ
2. `.env` дэх `CRON_SCHEDULE`-ийн дагуу давтан ажиллана
3. Бүх үйл ажиллагааг консол болон файл руу бүртгэнэ

### Гараар цуглуулалт хийх

Бүх цуглуулагчийг нэг удаа ажиллуулах:

```bash
python -m app.services.scraper_service
```

Тодорхой банкны цуглуулагчийг ажиллуулах:

```bash
python app/crawlers/khanbank.py
python app/crawlers/arigbank.py
# ... гэх мэт
```

## 📡 API эндпойнтууд

### Өгөгдлийн сангийн эндпойнтууд

#### GET `/rates`

Өгөгдлийн сангаас бүх ханшийг хуудаслалттайгаар авах.

**Query параметрүүд:**

- `skip` (int, үндсэн: 0): Алгасах бичлэгийн тоо
- `limit` (int, үндсэн: 100, хамгийн их: 1000): Буцаах бичлэгийн хамгийн их тоо

**Жишээ:**

```bash
curl http://localhost:8000/rates?skip=0&limit=10
```

#### GET `/rates/latest`

Банк бүрийн хамгийн сүүлийн ханшийг авах.

**Жишээ:**

```bash
curl http://localhost:8000/rates/latest
```

#### GET `/rates/bank/{bank_name}`

Тодорхой банкны ханшийг авах.

**Параметрүүд:**

- `bank_name`: Банкны нэр (жишээ нь: KhanBank, ArigBank)

**Жишээ:**

```bash
curl http://localhost:8000/rates/bank/KhanBank
curl http://localhost:8000/rates/bank/ArigBank?limit=5
```

#### GET `/rates/date/{date}`

Тодорхой өдрийн ханшийг авах.

**Параметрүүд:**

- `date`: YYYY-MM-DD форматтай огноо

**Жишээ:**

```bash
curl http://localhost:8000/rates/date/2025-01-15
```

#### GET `/rates/bank/{bank_name}/date/{date}`

Тодорхой банк ба огнооны ханшийг авах.

**Жишээ:**

```bash
curl http://localhost:8000/rates/bank/KhanBank/date/2025-01-15
```

### Скрэйпинг эндпойнтууд

#### POST `/scrape/all`

Бүх банкаас ханш цуглуулж өгөгдлийн санд хадгална.

**Жишээ:**

```bash
curl -X POST http://localhost:8000/scrape/all
curl -X POST "http://localhost:8000/scrape/all?date=2025-01-15"
```

#### GET `/scrape/bank/{bank_name}`

Тодорхой банкаас шууд ханш цуглуулж буцаана (өгөгдлийн санд хадгалахгүй).

**Параметрүүд:**

- `bank_name`: Банкны нэр (том жижиг үсэг ялгахгүй)
  - Дэмжигдсэн: KhanBank, GolomtBank, Golomt, MongolBank, TDBM, XacBank, ArigBank, BogdBank, StateBank, CapitronBank, TransBank, NIBank, MBank, CKBank

**Жишээ:**

```bash
curl http://localhost:8000/scrape/bank/KhanBank
curl "http://localhost:8000/scrape/bank/ArigBank?date=2025-01-15"
```

## 🗄️ Өгөгдлийн сангийн тохиргоо

Систем нь SQLAlchemy-ээр дамжуулан олон төрлийн өгөгдлийн санг дэмждэг.

### SQLite (Үндсэн)

```bash
DATABASE_URL=sqlite:///./exchange_rates.db
```

### PostgreSQL

```bash
DATABASE_URL=postgresql://username:password@localhost:5432/exchange_rates
```

**PostgreSQL драйвер суулгах:**

```bash
pip install psycopg2-binary
```

### MySQL

```bash
DATABASE_URL=mysql://username:password@localhost:3306/exchange_rates
```

**MySQL драйвер суулгах:**

```bash
pip install pymysql
```

## ⏰ Хуваарийн тохиргоо

`CRON_SCHEDULE` орчны хувьсагч стандарт cron форматыг ашигладаг:

```bash
минут цаг өдөр сар долоо_хоног
```

**Жишээнүүд:**

| Хуваарь | Тайлбар |
|---------|---------|
| `0 1 * * *` | Өдөр бүр 01:00 цагт (үндсэн) |
| `0 */6 * * *` | 6 цаг тутамд |
| `0 9 * * 1-5` | Ажлын өдрүүдэд 09:00 цагт |
| `30 14 * * *` | Өдөр бүр 14:30 цагт |
| `0 0 1 * *` | Сар бүрийн 1-нд шөнө дундын 00:00 цагт |

## 📊 Өгөгдлийн загвар

### CurrencyRate (Өгөгдлийн сангийн загвар)

```python
{
    "id": 1,
    "bank_name": "KhanBank",
    "date": "2025-01-15",
    "rates": {
        "USD": {
            "cash": {"buy": 3400.0, "sell": 3440.0},
            "noncash": {"buy": 3405.0, "sell": 3435.0}
        },
        "EUR": {
            "cash": {"buy": 3800.0, "sell": 3850.0},
            "noncash": {"buy": 3810.0, "sell": 3840.0}
        }
        // ... бусад валютууд
    },
    "timestamp": "2025-01-15T10:30:00"
}
```

### Ханшийн бүтэц

Валют бүр хоёр төрлийн ханштай:

- **Бэлэн**: Бэлэн мөнгөний ханш
  - `buy`: Банкны худалдан авах ханш
  - `sell`: Банкны худалдах ханш
- **Бэлэн бус**: Цахим шилжүүлгийн ханш
  - `buy`: Банкны худалдан авах ханш
  - `sell`: Банкны худалдах ханш

## 🔍 Бүртгэл

Дараах үйл ажиллагааг автоматаар бүртгэнэ:

- Амжилттай цуглуулалтууд
- Алдаатай цуглуулалтууд болон дэлгэрэнгүй мэдээлэл
- API хүсэлтүүд
- Хуваарийн ажлууд

Бүртгэлүүд консол болон файлд (`app/utils/logger.py`-д тохируулсан) бичигдэнэ.

## 🐳 Docker-оор байршуулах (Сонголт)

`Dockerfile` үүсгэх:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN playwright install chromium
RUN playwright install-deps chromium

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

`docker-compose.yml` үүсгэх:

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/exchange_rates
    depends_on:
      - db
    volumes:
      - ./.env:/app/.env

  db:
    image: postgres:13
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=exchange_rates
    volumes:
      - postgres_data:/var/lib/postgresql/data

  cron:
    build: .
    command: python cron.py
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/exchange_rates
    depends_on:
      - db
    volumes:
      - ./.env:/app/.env

volumes:
  postgres_data:
```

Docker-оор ажиллуулах:

```bash
docker-compose up -d
```

## 🧪 Туршилт

Тодорхой цуглуулагчийг ажиллуулах:

```bash
PYTHONPATH=. python app/crawlers/khanbank.py
```

API-г турших:

```bash
# API серверийг эхлүүлэх
uvicorn app.api.main:app --reload

# Өөр терминалд эндпойнтуудыг турших
curl http://localhost:8000/
curl http://localhost:8000/scrape/bank/KhanBank
curl http://localhost:8000/rates/latest
```

## 🛠️ Хөгжүүлэлт

### Төслийн бүтэц

```bash
mongolian-bank-exchange-rate/
├── app/
│   ├── api/
│   │   └── main.py              # FastAPI програм
│   ├── crawlers/                # Банк тус бүрийн цуглуулагч (13 банк)
│   │   ├── base_crawler.py      # Үндсэн цуглуулагчийн загвар
│   │   ├── khanbank.py
│   │   ├── arigbank.py
│   │   └── ...
│   ├── db/
│   │   ├── database.py          # Өгөгдлийн сангийн тохиргоо
│   │   └── repository.py        # Өгөгдлийн сангийн үйлдлүүд
│   ├── models/
│   │   ├── currency.py          # SQLAlchemy загварууд
│   │   └── exchange_rate.py     # Pydantic загварууд
│   ├── services/
│   │   └── scraper_service.py   # Цуглуулагчдыг зохицуулагч
│   ├── utils/
│   │   └── logger.py            # Бүртгэлийн тохиргоо
│   └── config.py                # Тохиргооны удирдлага
├── cron.py                      # Хуваарийн цуглуулагч
├── .env                         # Орчны тохиргоо
├── requirements.txt             # Python хамаарлууд
└── README.md                    # Энэ файл
```

### Шинэ банк нэмэх

1. `app/crawlers/`-д шинэ цуглуулагч үүсгэх:

    ```python
    from app.crawlers.base_crawler import BaseCrawler
    from app.models.exchange_rate import CurrencyDetail, Rate
    from typing import Dict

    class NewBankCrawler(BaseCrawler):
        """NewBank-ны ханшийн цуглуулагч."""
        
        BANK_NAME = "NewBank"
        
        def crawl(self) -> Dict[str, CurrencyDetail]:
            # Цуглуулах логикийг хэрэгжүүлэх
            pass
    ```

2. `.env` файлд банкны URI нэмэх:

    ```bash
    NEWBANK_URI=https://newbank.mn/rates
    ```

3. `app/config.py`-д нэмэх:

    ```python
    NEWBANK_URI: str = os.getenv("NEWBANK_URI", "https://newbank.mn/rates")
    ```

4. `app/services/scraper_service.py`-д нэмэх:

    ```python
    from app.crawlers.newbank import NewBankCrawler

    # __init__ дотор:
    NewBankCrawler(config.NEWBANK_URI, self.date),

    # scrape_bank дотор:
    "newbank": lambda: NewBankCrawler(config.NEWBANK_URI, self.date),
    ```

## 📝 Лиценз

Энэ төсөл MIT лицензтэй - дэлгэрэнгүй мэдээллийг [LICENSE](LICENSE) файлаас харна уу.