# 🏦 Монголын Банкуудын Валютын Ханш API

Монголын 13 банкны валютын ханшийг цуглуулж, API-аар үйлчилдэг нээлттэй эхийн төсөл.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## Онцлогууд

- 13 арилжааны банкны валютын ханш
- Өдөр бүр автоматаар шинэчлэгдэнэ (09:00 UTC+8)
- FastAPI дээр суурилсан REST API
- Docker дэмжлэгтэй
- Өмнөх ханшуудын түүж авч хадгална
- API Documentation-тэй. [OPEN API DOC](https://mongolian-bank-exchange-rate-6620c122ff22.herokuapp.com/docs)

## Дэмжигдсэн Банкууд

| Банк               | Код           | Төрөл      |
|--------------------|---------------|------------|
| Хаан Банк          | KhanBank      | HTTP       |
| Голомт Банк        | GolomtBank    | HTTP       |
| Хас Банк           | XacBank       | HTTP       |
| Ариг Банк          | ArigBank      | HTTP       |
| Төрийн Банк        | StateBank     | HTTP       |
| Монгол Банк        | MongolBank    | HTTP       |
| Капитрон Банк      | CapitronBank  | HTTP       |
| ХХБ                | TDBM          | Playwright |
| Богд Банк          | BogdBank      | Playwright |
| Чингис Хаан Банк   | CKBank        | Playwright |
| ҮХОБ               | NIBank        | Playwright |
| Транс Банк         | TransBank     | Playwright |
| М Банк             | MBank         | Playwright |

## API endpoint-ууд

| Эцсийн цэг                            | Тайлбар                   |
|---------------------------------------|---------------------------|
| `GET /`                               | API мэдээлэл              |
| `GET /health`                         | API health check          |
| `GET /rates`                          | Бүх ханш (хуудаслалттай)  |
| `GET /rates/latest`                   | Хамгийн сүүлийн ханш      |
| `GET /rates/bank/{bank}`              | Банкны ханш               |
| `GET /rates/date/{date}`              | Өдрийн ханш               |
| `GET /rates/bank/{bank}/date/{date}`  | Банк, өдрийн ханш         |

## Суулгах

### Docker

```bash
git clone https://github.com/btseee/mongolian-bank-exchange-rate.git
cd mongolian-bank-exchange-rate
docker-compose up -d
```

API: [http://localhost:8000](http://localhost:8000)  
Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### Local

```bash
git clone https://github.com/btseee/mongolian-bank-exchange-rate.git
cd mongolian-bank-exchange-rate

python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
playwright install chromium

# API эхлүүлэх
uvicorn app.api.api:app --reload

# Cron ажиллуулах (өөр терминалд)
python scripts/cron.py
```

## Орчны Хувьсагчууд

| Хувьсагч                  | Анхдагч                           | Тайлбар               |
|---------------------------|-----------------------------------|-----------------------|
| `DATABASE_URL`            | `sqlite:///./exchange_rates.db`   | Өгөгдлийн сангийн URL |
| `CRON_SCHEDULE`           | `0 9 * * *`                       | Cron хуваарь          |
| `SSL_VERIFY`              | `false`                           | SSL баталгаажуулалт   |
| `ENABLE_PARALLEL`         | `true`                            | Зэрэгцээ ажиллуулах   |
| `MAX_WORKERS`             | `8`                               | HTTP worker тоо       |
| `PLAYWRIGHT_MAX_WORKERS`  | `3`                               | Playwright worker     |

## Хөгжүүлэлт

```bash
# Тест ажиллуулах
pytest

# Код форматлах
black .
isort .
```

## Хувь Нэмэр Оруулах

[CONTRIBUTING.md](CONTRIBUTING.md) үзнэ үү.

## Лиценз

MIT License - [LICENSE.md](LICENSE.md)

## Холбогдох

- GitHub: [@btseee](https://github.com/btseee)
- Email: [bbattseren88@gmail.com](mailto:bbattseren88@gmail.com)
- Дэмжих: [Buy Me a Coffee](https://buymeacoffee.com/btseee)
