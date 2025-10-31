"""
Crawler for TransBank exchange rates (uses Playwright).
"""

import json
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


class TransBankCrawler:
    """Crawler to fetch exchange rates from TransBank website."""

    BANK_NAME = "TransBank"
    REQUEST_TIMEOUT = 60000

    def __init__(self, url: str, date: str):
        """
        Initialize the crawler.

        Args:
            url: Bank website URL
            date: Date in YYYY-MM-DD format
        """
        self.url = url
        self.date = date
        self.ssl_verify = os.getenv("SSL_VERIFY", "True").lower() in ("true", "1", "t")

    def crawl(self) -> Dict[str, CurrencyDetail]:
        """
        Fetch exchange rates from the TransBank website.

        Returns:
            Mapping of currency code -> CurrencyDetail
        """
        logger.info(f"Fetching rates from {self.BANK_NAME}: {self.url}")

        try:
            url_with_date = f"{self.url}?startdate={self.date}" if "?" not in self.url else self.url

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                page.goto(url_with_date, timeout=self.REQUEST_TIMEOUT, wait_until="networkidle")

                # Wait for the table to load
                page.wait_for_selector("table", timeout=self.REQUEST_TIMEOUT)

                # Extract data from Next.js __NEXT_DATA__ script
                next_data_script = page.locator("script#__NEXT_DATA__").first
                if next_data_script:
                    json_text = next_data_script.inner_text()
                    data = json.loads(json_text)
                    rates = self._parse_next_data(data)
                else:
                    # Fallback to table scraping
                    rates = self._parse_table(page)

                browser.close()

                logger.info(f"Successfully fetched {len(rates)} currencies from {self.BANK_NAME}")
                return rates

        except TimeoutError:
            logger.error(f"Timeout while fetching from {self.BANK_NAME}")
            raise
        except Exception as e:
            logger.error(f"Error while crawling {self.BANK_NAME}: {e}")
            raise

    def _parse_next_data(self, data: dict) -> Dict[str, CurrencyDetail]:
        rates = {}

        try:
            rate_data = data.get("props", {}).get("pageProps", {}).get("rateData", {})

            for date_key, currencies in rate_data.items():
                for currency_code, currency_data in currencies.items():
                    if currency_code == "NAME":
                        continue

                    code = currency_code.strip().lower()

                    # Extract cash rates (type 2)
                    cash_data = currency_data.get("2", {})
                    cash_buy = self._parse_float(cash_data.get("BUY_RATE"))
                    cash_sell = self._parse_float(cash_data.get("SELL_RATE"))

                    # Extract non-cash rates (type 3)
                    noncash_data = currency_data.get("3", {})
                    noncash_buy = self._parse_float(noncash_data.get("BUY_RATE"))
                    noncash_sell = self._parse_float(noncash_data.get("SELL_RATE"))

                    rates[code] = CurrencyDetail(
                        cash=Rate(buy=cash_buy, sell=cash_sell), noncash=Rate(buy=noncash_buy, sell=noncash_sell)
                    )

        except Exception as e:
            logger.error(f"Error parsing Next.js data: {e}")
            raise

        return rates

    def _parse_table(self, page) -> Dict[str, CurrencyDetail]:
        rates = {}

        try:
            table = page.locator("table").first
            rows = table.locator("tbody tr").all()

            for row in rows:
                cells = row.locator("td").all()
                if len(cells) < 7:
                    continue

                try:
                    # First cell contains currency code like "USD"
                    currency_text = cells[0].inner_text().strip()
                    # Extract just the currency code (first word)
                    currency_code = currency_text.split()[0].lower()

                    if not currency_code or len(currency_code) > 10:
                        continue

                    # Format: Currency | Name | Mongol Bank | Cash Buy | Cash Sell | Non-cash Buy | Non-cash Sell
                    cash_buy = self._parse_float(cells[3].inner_text())
                    cash_sell = self._parse_float(cells[4].inner_text())
                    noncash_buy = self._parse_float(cells[5].inner_text())
                    noncash_sell = self._parse_float(cells[6].inner_text())

                    rates[currency_code] = CurrencyDetail(
                        cash=Rate(buy=cash_buy, sell=cash_sell), noncash=Rate(buy=noncash_buy, sell=noncash_sell)
                    )
                except (ValueError, IndexError) as e:
                    logger.warning(f"Error parsing row: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error parsing table: {e}")
            raise

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
