"""
Crawler for Trade and Development Bank (TDBM) exchange rates (uses Playwright).
"""

import os
import time
from datetime import datetime, timedelta
from typing import Dict, Optional

import urllib3
from dotenv import load_dotenv
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from app.config import config
from app.models.exchange_rate import CurrencyDetail, Rate
from app.utils.logger import get_logger

logger = get_logger(__name__)


class TDBMCrawler:
    """Crawler to fetch exchange rates from TDBM website."""

    BANK_NAME = "TDBM"
    REQUEST_TIMEOUT = config.PLAYWRIGHT_TIMEOUT

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
        self.request_timeout = config.PLAYWRIGHT_TIMEOUT

    def crawl(self) -> Dict[str, CurrencyDetail]:
        """
        Fetch exchange rates from the TDBM website.

        Returns:
            Mapping of currency code -> CurrencyDetail
        """
        logger.info(f"Fetching rates from {self.BANK_NAME}: {self.url}")

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(ignore_https_errors=not self.ssl_verify)
                context.set_default_timeout(self.request_timeout)
                page = context.new_page()

                self._navigate_with_retries(page)

                # Find and set date to yesterday if today has no data
                date_inputs = page.locator("input[type=date]").all()
                if date_inputs:
                    # Try today first
                    today = datetime.now().strftime("%Y-%m-%d")
                    date_inputs[0].fill(today)

                    # Click submit button to load data
                    buttons = page.locator("form button, form input[type=submit]").all()
                    if buttons:
                        buttons[0].click()
                        page.wait_for_selector("table.table-hover", state="visible", timeout=self.request_timeout)

                    # Check if we have data
                    rates = self._parse_rates(page)

                    # If no rates, try yesterday
                    if not rates:
                        logger.info(f"{self.BANK_NAME} has no data for today, trying yesterday")
                        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
                        date_inputs[0].fill(yesterday)
                        if buttons:
                            buttons[0].click()
                            page.wait_for_selector("table.table-hover", state="visible", timeout=self.request_timeout)
                        rates = self._parse_rates(page)
                else:
                    rates = self._parse_rates(page)

                browser.close()

            logger.info(f"Successfully fetched {len(rates)} currencies from {self.BANK_NAME}")
            return rates

        except PlaywrightTimeoutError:
            logger.error(f"Request timeout while fetching from {self.BANK_NAME}")
            raise
        except Exception as e:
            logger.error(f"Failed to fetch rates from {self.BANK_NAME}: {e}")
            raise

    def _parse_rates(self, page) -> Dict[str, CurrencyDetail]:
        rates = {}
        rows = page.locator("table.table-hover tbody tr").all()

        for row in rows:
            cells = row.locator("td").all()

            if len(cells) >= 8:
                try:
                    currency_code = cells[1].inner_text().strip().lower()

                    if not currency_code or len(currency_code) != 3:
                        continue

                    # Mongol Bank column present but not used in calculations
                    self._parse_float(cells[3].inner_text())
                    noncash_buy = self._parse_float(cells[4].inner_text())
                    noncash_sell = self._parse_float(cells[5].inner_text())
                    cash_buy = self._parse_float(cells[6].inner_text())
                    cash_sell = self._parse_float(cells[7].inner_text())

                    rates[currency_code] = CurrencyDetail(
                        cash=Rate(buy=cash_buy if cash_buy else 0.0, sell=cash_sell if cash_sell else 0.0),
                        noncash=Rate(
                            buy=noncash_buy if noncash_buy else 0.0, sell=noncash_sell if noncash_sell else 0.0
                        ),
                    )
                except Exception as e:
                    logger.debug(f"Skipping row due to parsing error: {e}")
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

    def _navigate_with_retries(self, page):
        attempts = 0
        last_err = None
        while attempts < 2:
            try:
                wait_until = "domcontentloaded" if attempts == 0 else "load"
                logger.debug(f"Navigating to {self.url} (attempt {attempts+1}, wait_until={wait_until})")
                page.goto(self.url, timeout=self.request_timeout, wait_until=wait_until)
                page.wait_for_selector("table.table-hover", timeout=self.request_timeout)
                return
            except PlaywrightTimeoutError as e:
                last_err = e
                attempts += 1
                try:
                    page.reload(timeout=self.request_timeout, wait_until="load")
                except Exception:
                    pass
        raise last_err if last_err else PlaywrightTimeoutError("Navigation timeout")


if __name__ == "__main__":
    url = os.getenv("TDBM_URI", "https://www.tdbm.mn/en/exchange")
    crawler = TDBMCrawler(url=url, date="")
    try:
        rates = crawler.crawl()
        if len(rates) == 0:
            print("TDBM has no rates available")
        else:
            print(f"Successfully fetched rates for {len(rates)} currencies")
            for currency, details in rates.items():
                print(
                    f"{currency.upper()}: Cash Buy={details.cash.buy}, Cash Sell={details.cash.sell}, "
                    f"Non-Cash Buy={details.noncash.buy}, Non-Cash Sell={details.noncash.sell}"
                )
    except Exception as e:
        print(f"Error: {e}")
