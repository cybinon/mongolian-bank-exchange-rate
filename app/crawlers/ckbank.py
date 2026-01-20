import os
from typing import Dict

import urllib3
from dotenv import load_dotenv
from playwright.sync_api import TimeoutError, sync_playwright

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from app.models.exchange_rate import CurrencyDetail, Rate
from app.utils.logger import get_logger

logger = get_logger(__name__)


class CKBankCrawler:
    BANK_NAME = "CKBank"
    REQUEST_TIMEOUT = 60000

    def __init__(self, url: str, date: str):
        self.url = url
        self.date = date
        self.ssl_verify = os.getenv("SSL_VERIFY", "True").lower() in ("true", "1", "t")

    def crawl(self) -> Dict[str, CurrencyDetail]:
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                page.goto(self.url, timeout=self.REQUEST_TIMEOUT, wait_until="networkidle")
                page.wait_for_selector("table", timeout=self.REQUEST_TIMEOUT)

                rates = self._parse_rates(page)
                browser.close()

                return rates

        except TimeoutError:
            logger.error(f"Timeout while fetching from {self.BANK_NAME}")
            raise
        except Exception as e:
            logger.error(f"Error while crawling {self.BANK_NAME}: {e}")
            raise

    def _parse_rates(self, page) -> Dict[str, CurrencyDetail]:
        rates = {}

        try:
            table = page.locator("table").first
            rows = table.locator("tr").all()

            for i, row in enumerate(rows):
                if i < 2:
                    continue

                cells = row.locator("td").all()
                if len(cells) < 6:
                    continue

                try:
                    currency_code = cells[0].inner_text().strip().replace("\xa0", "").lower()

                    if not currency_code or len(currency_code) > 10:
                        continue

                    cash_buy = self._parse_float(cells[2].inner_text())
                    cash_sell = self._parse_float(cells[3].inner_text())
                    noncash_buy = self._parse_float(cells[4].inner_text())
                    noncash_sell = self._parse_float(cells[5].inner_text())

                    rates[currency_code] = CurrencyDetail(
                        cash=Rate(buy=cash_buy, sell=cash_sell), noncash=Rate(buy=noncash_buy, sell=noncash_sell)
                    )
                except (ValueError, IndexError) as e:
                    logger.warning(f"Error parsing row {i}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error parsing table: {e}")
            raise

        return rates

    def _parse_float(self, value: str) -> float:
        try:
            cleaned = value.strip().replace(",", "").replace(" ", "").replace("\xa0", "")
            if not cleaned or cleaned == "-":
                return None
            return float(cleaned)
        except ValueError:
            return None
