"""
Exchange rate crawler for M-Bank (using Playwright).
"""

import os
import re
from typing import Dict
from dotenv import load_dotenv
import urllib3
from playwright.sync_api import sync_playwright, TimeoutError

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from app.models.exchange_rate import Rate, CurrencyDetail
from app.utils.logger import get_logger

logger = get_logger(__name__)


class MBankCrawler:
    """Crawler for fetching exchange rates from M-Bank's website."""

    BANK_NAME = "M-Bank"
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
        Fetch exchange rates from M-Bank.

        Returns:
            Dict mapping currency code -> CurrencyDetail object
        """
        logger.info(f"Fetching rates from {self.BANK_NAME}: {self.url}")

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                page.goto(self.url, timeout=self.REQUEST_TIMEOUT, wait_until="networkidle")

                # Extract exchange rate data from page content
                rates = self._extract_rates_from_page(page)

                browser.close()

                logger.info(f"Successfully fetched {len(rates)} currencies from {self.BANK_NAME}")
                return rates

        except TimeoutError:
            logger.error(f"Timeout while fetching from {self.BANK_NAME}")
            raise
        except Exception as e:
            logger.error(f"Error while crawling {self.BANK_NAME}: {e}")
            raise

    def _extract_rates_from_page(self, page) -> Dict[str, CurrencyDetail]:
        rates = {}

        try:
            # M-Bank stores exchange rates in the page content
            # Look for USD, EUR and other currency codes in the text
            content = page.content()

            # Common currencies to check
            currencies = ["USD", "EUR", "CNY", "JPY", "RUB", "KRW", "GBP", "CHF", "HKD", "SGD"]

            for currency_code in currencies:
                try:
                    # Search for currency pattern in page
                    # Pattern might be: USD ... numbers (buy/sell rates)
                    pattern = rf"{currency_code}.*?(\d{{1,5}}\.?\d{{0,2}})"
                    matches = re.findall(pattern, content, re.DOTALL)

                    if len(matches) >= 2:
                        # Usually: cash buy, cash sell, noncash buy, noncash sell
                        cash_buy = self._parse_float(matches[0])
                        cash_sell = self._parse_float(matches[1])
                        noncash_buy = self._parse_float(matches[2]) if len(matches) > 2 else cash_buy
                        noncash_sell = self._parse_float(matches[3]) if len(matches) > 3 else cash_sell

                        rates[currency_code.lower()] = CurrencyDetail(
                            cash=Rate(buy=cash_buy, sell=cash_sell), noncash=Rate(buy=noncash_buy, sell=noncash_sell)
                        )
                except Exception as e:
                    logger.warning(f"Error parsing {currency_code}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error extracting rates: {e}")
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
