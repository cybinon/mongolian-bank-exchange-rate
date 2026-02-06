# Хувь Нэмэр Оруулах Заавар

Энэхүү төсөлд хувь нэмэр оруулахыг хүсч байгаад баярлалаа! 🎉

## Хэрхэн Хувь Нэмэр Оруулах Вэ?

### 1. Issue Нээх

- Алдаа олсон бол **Bug Report** template ашиглан issue нээнэ үү
- Шинэ санаа байвал **Feature Request** template ашиглана уу
- Issue нээхийн өмнө ижил issue байгаа эсэхийг шалгана уу

### 2. Pull Request Илгээх

#### Эхлэх

```bash
# Fork хийх (GitHub дээр)

# Clone хийх
git clone https://github.com/ТАНЫ_ХЭРЭГЛЭГЧИЙН_НЭР/mongolian-bank-exchange-rate.git
cd mongolian-bank-exchange-rate

# Upstream remote нэмэх
git remote add upstream https://github.com/btseee/mongolian-bank-exchange-rate.git

# Virtual environment үүсгэх
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Dependencies суулгах
pip install -r requirements.txt
playwright install chromium
```

#### Branch Үүсгэх

```bash
# main branch-аас шинэ branch үүсгэх
git checkout main
git pull upstream main
git checkout -b feature/таны-өөрчлөлт
```

#### Өөрчлөлт Хийх

1. Код бичих
2. Test бичих (шаардлагатай бол)
3. `pytest` ажиллуулж шалгах
4. `black .` болон `isort .` ажиллуулах

#### Commit Хийх

```bash
git add .
git commit -m "feat: шинэ функц нэмсэн"
```

**Commit message формат:**

- `feat:` - Шинэ функц
- `fix:` - Алдаа засах
- `docs:` - Баримт бичиг
- `refactor:` - Код сайжруулах
- `test:` - Тест нэмэх

#### Pull Request Илгээх

```bash
git push origin feature/таны-өөрчлөлт
```

GitHub дээр Pull Request нээнэ үү.

## Код Стандарт

- **Python 3.8+** ашиглана
- **Black** formatter (line-length=120)
- **isort** import эрэмбэлэх
- Type hints ашиглах
- Docstring бичих (English)
- Test бичих

## Шинэ Банк Нэмэх

Шинэ банк нэмэхийн тулд:

1. `app/crawlers/http_crawlers.py` эсвэл `playwright_crawlers.py` дотор class үүсгэх
2. `BaseCrawler` эсвэл `PlaywrightCrawler`-аас удамших
3. `app/crawlers/__init__.py`-д нэмэх
4. `app/config.py`-д URI нэмэх
5. Test бичих

Жишээ:

```python
from app.crawlers.base import BaseCrawler

class NewBank(BaseCrawler):
    BANK_NAME = "NewBank"

    def crawl(self):
        resp = self.get("https://api.newbank.mn/rates")
        resp.raise_for_status()
        return self._parse(resp.json())

    def _parse(self, data):
        rates = {}
        # Parse logic here
        return rates
```

## Тест Ажиллуулах

```bash
# Бүх тест
pytest

# Coverage-тай
pytest --cov=app

# Тодорхой тест
pytest tests/test_crawlers.py -v
```

## Асуулт Байвал

- Issue нээх
- Discussion эхлүүлэх
- Email: [bbattseren88@gmail.com](mailto:bbattseren88@gmail.com)

## Лиценз

Таны хувь нэмэр MIT лицензийн дор нийтлэгдэнэ.
