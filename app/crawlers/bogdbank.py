import os
import time
from datetime import date
from typing import Dict, Optional

import urllib3
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from app.models.exchange_rate import CurrencyDetail, Rate


class BogdBankCrawler:
    BANK_NAME = "BogdBank"
    REQUEST_TIMEOUT = 60000

    def __init__(self, url: str, date: str):
        self.url = url
        self.date = date
        self.ssl_verify = os.getenv("SSL_VERIFY", "True").lower() in ("true", "1", "t")

    def crawl(self) -> Dict[str, CurrencyDetail]:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(ignore_https_errors=not self.ssl_verify)
            page = context.new_page()

            # BogdBank doesn't support historical dates - only use date param for today
            today = date.today().isoformat()
            if self.date == today:
                url_with_date = f"{self.url}?date={self.date}"
            else:
                # For historical dates, just get current rates (no historical data available)
                url_with_date = self.url

            page.goto(url_with_date, timeout=self.REQUEST_TIMEOUT, wait_until="networkidle")
            page.wait_for_selector("table", timeout=self.REQUEST_TIMEOUT)
            time.sleep(2)

            rates = self._parse_rates(page)
            browser.close()

        return rates

    def _parse_rates(self, page) -> Dict[str, CurrencyDetail]:
        rates = {}
        rows = page.locator("table tbody tr").all()

        for row in rows:
            cells = row.locator("td").all()

            if len(cells) >= 6:
                try:
                    currency_text = cells[0].inner_text().strip()
                    currency_code = currency_text.replace("\xa0", "").replace(" ", "").lower()

                    if not currency_code or len(currency_code) < 3:
                        continue

                    cash_buy = self._parse_float(cells[2].inner_text())
                    cash_sell = self._parse_float(cells[3].inner_text())
                    noncash_buy = self._parse_float(cells[4].inner_text())
                    noncash_sell = self._parse_float(cells[5].inner_text())

                    rates[currency_code] = CurrencyDetail(
                        cash=Rate(buy=cash_buy if cash_buy else 0.0, sell=cash_sell if cash_sell else 0.0),
                        noncash=Rate(
                            buy=noncash_buy if noncash_buy else 0.0, sell=noncash_sell if noncash_sell else 0.0
                        ),
                    )
                except Exception:
                    continue

        return rates

    def _parse_float(self, value: str) -> Optional[float]:
        if not value or value == "-" or value.strip() == "":
            return None
        try:
            cleaned = value.replace(",", "").strip()
            return float(cleaned)
        except ValueError:
            return None
