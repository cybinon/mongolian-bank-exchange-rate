import os
import re
from typing import Dict

import urllib3
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from app.models.exchange_rate import CurrencyDetail, Rate


class NIBankCrawler:
    BANK_NAME = "NIBank"
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
            page.wait_for_selector(".exchange-block", timeout=self.REQUEST_TIMEOUT)

            rates = self._parse_exchange_blocks(page)
            browser.close()

            return rates

    def _parse_exchange_blocks(self, page) -> Dict[str, CurrencyDetail]:
        rates = {}
        blocks = page.locator(".exchange-block").all()

        for block in blocks:
            try:
                text = block.inner_text()
                lines = [line.strip() for line in text.split("\n") if line.strip()]

                if len(lines) < 6:
                    continue

                currency_line = lines[0]
                currency_match = re.match(r"^([A-Z]{3})", currency_line)
                if not currency_match:
                    continue

                currency_code = currency_match.group(1).lower()

                cash_buy = None
                cash_sell = None
                noncash_buy = None
                noncash_sell = None

                for i, line in enumerate(lines):
                    if "Бэлэн авах" in line and i + 1 < len(lines):
                        cash_buy = self._parse_float(lines[i + 1])
                    elif "Бэлэн зарах" in line and i + 1 < len(lines):
                        cash_sell = self._parse_float(lines[i + 1])
                    elif "Бэлэн бус авах" in line and i + 1 < len(lines):
                        noncash_buy = self._parse_float(lines[i + 1])
                    elif "Бэлэн бус за" in line and i + 1 < len(lines):
                        noncash_sell = self._parse_float(lines[i + 1])

                rates[currency_code] = CurrencyDetail(
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
