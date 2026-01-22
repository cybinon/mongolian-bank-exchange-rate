import os
import re
from typing import Dict

import urllib3
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from app.models.exchange_rate import CurrencyDetail, Rate


class MBankCrawler:
    BANK_NAME = "M-Bank"
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
        currencies = ["USD", "EUR", "CNY", "JPY", "RUB", "KRW", "GBP", "CHF", "HKD", "SGD"]

        for currency_code in currencies:
            try:
                pattern = rf"{currency_code}.*?(\d{{1,5}}\.?\d{{0,2}})"
                matches = re.findall(pattern, content, re.DOTALL)

                if len(matches) >= 2:
                    cash_buy = self._parse_float(matches[0])
                    cash_sell = self._parse_float(matches[1])
                    noncash_buy = self._parse_float(matches[2]) if len(matches) > 2 else cash_buy
                    noncash_sell = self._parse_float(matches[3]) if len(matches) > 3 else cash_sell

                    rates[currency_code.lower()] = CurrencyDetail(
                        cash=Rate(buy=cash_buy, sell=cash_sell), noncash=Rate(buy=noncash_buy, sell=noncash_sell)
                    )
            except Exception:
                continue

        return rates

    def _parse_float(self, value) -> float:
        try:
            if isinstance(value, (int, float)):
                return float(value) if value != 0 else None

            cleaned = str(value).strip().replace(",", "").replace(" ", "").replace("\xa0", "")
            if not cleaned or cleaned == "-" or cleaned == "0":
                return None
            return float(cleaned)
        except (ValueError, TypeError):
            return None
