import os
import re
from typing import Dict, Optional

import urllib3
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from app.models.exchange_rate import CurrencyDetail, Rate


class CKBankCrawler:
    BANK_NAME = "Chinggis Khaan Bank"
    REQUEST_TIMEOUT = 60000

    def __init__(self, url: str, date: str):
        self.url = url
        self.date = date
        self.ssl_verify = os.getenv("SSL_VERIFY", "True").lower() in ("true", "1", "t")

    def crawl(self) -> Dict[str, CurrencyDetail]:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto(self.url, timeout=self.REQUEST_TIMEOUT, wait_until="networkidle")

            rates = self._extract_rates_from_page(page)
            browser.close()

            return rates

    def _extract_rates_from_page(self, page) -> Dict[str, CurrencyDetail]:
        rates = {}
        content = page.content()

        patterns = [
            (r"USD.*?(\d{4}\.?\d{0,2}).*?(\d{4}\.?\d{0,2})", "usd"),
            (r"EUR.*?(\d{4}\.?\d{0,2}).*?(\d{4}\.?\d{0,2})", "eur"),
            (r"CNY.*?(\d{3}\.?\d{0,2}).*?(\d{3}\.?\d{0,2})", "cny"),
            (r"JPY.*?(\d{1,4}\.?\d{0,2}).*?(\d{1,4}\.?\d{0,2})", "jpy"),
            (r"RUB.*?(\d{1,4}\.?\d{0,2}).*?(\d{1,4}\.?\d{0,2})", "rub"),
            (r"KRW.*?(\d{1,4}\.?\d{0,2}).*?(\d{1,4}\.?\d{0,2})", "krw"),
            (r"GBP.*?(\d{4}\.?\d{0,2}).*?(\d{4}\.?\d{0,2})", "gbp"),
        ]

        for pattern, currency_code in patterns:
            try:
                match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
                if match:
                    cash_buy = self._parse_float(match.group(1))
                    cash_sell = self._parse_float(match.group(2))

                    rates[currency_code] = CurrencyDetail(
                        cash=Rate(buy=cash_buy, sell=cash_sell), noncash=Rate(buy=cash_buy, sell=cash_sell)
                    )
            except Exception:
                continue

        return rates

    def _parse_float(self, value) -> Optional[float]:
        try:
            if isinstance(value, (int, float)):
                return float(value) if value != 0 else None

            cleaned = str(value).strip().replace(",", "").replace(" ", "").replace("\xa0", "")
            if not cleaned or cleaned == "-" or cleaned == "0":
                return None
            return float(cleaned)
        except (ValueError, TypeError):
            return None
