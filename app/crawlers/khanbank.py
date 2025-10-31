"""
Crawler for Khan Bank exchange rates.
"""

import datetime
import os
from typing import Dict, Optional

import requests
import urllib3
from dotenv import load_dotenv

load_dotenv()

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from app.models.exchange_rate import CurrencyDetail, Rate
from app.utils.logger import get_logger

logger = get_logger(__name__)


class KhanBankCrawler:
    """Crawler to fetch exchange rates from Khan Bank API."""

    BANK_NAME = "KhanBank"
    REQUEST_TIMEOUT = 30  # seconds

    def __init__(self, url: str, date: str):
        """
        Initialize the crawler.

        Args:
            url: Bank API URL
            date: Date in YYYY-MM-DD format
        """
        self.url = url
        self.date = date
        self.ssl_verify = os.getenv("SSL_VERIFY", "True").lower() in ("true", "1", "t")

    def crawl(self) -> Dict[str, CurrencyDetail]:
        """
        Fetch exchange rates from Khan Bank API.

        Returns:
            Mapping of currency code -> CurrencyDetail
        """
        endpoint = f"{self.url}?date={self.date}"
        logger.info(f"Fetching rates from {self.BANK_NAME}: {endpoint}")

        try:
            response = requests.get(url=endpoint, verify=self.ssl_verify, timeout=self.REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()

            if not isinstance(data, list):
                raise ValueError(f"Expected list response, got {type(data)}")

            rates = self._parse_rates(data)
            logger.info(f"Successfully fetched {len(rates)} currencies from {self.BANK_NAME}")
            return rates

        except requests.exceptions.Timeout:
            logger.error(f"Request timeout while fetching from {self.BANK_NAME}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {self.BANK_NAME}: {e}")
            raise
        except (ValueError, KeyError) as e:
            logger.error(f"Failed to parse response from {self.BANK_NAME}: {e}")
            raise

    def _parse_rates(self, data: list) -> Dict[str, CurrencyDetail]:
        rates = {}

        for item in data:
            currency_code = item.get("currency")
            if not currency_code:
                logger.warning(f"Skipping item with missing currency code: {item}")
                continue

            try:
                rates[currency_code.lower()] = CurrencyDetail(
                    cash=Rate(
                        buy=self._parse_rate_value(item.get("cashBuyRate")),
                        sell=self._parse_rate_value(item.get("cashSellRate")),
                    ),
                    noncash=Rate(
                        buy=self._parse_rate_value(item.get("buyRate")),
                        sell=self._parse_rate_value(item.get("sellRate")),
                    ),
                )
            except Exception as e:
                logger.warning(f"Failed to parse rates for {currency_code}: {e}")
                continue

        return rates

    @staticmethod
    def _parse_rate_value(value) -> Optional[float]:
        if value is None:
            return None

        try:
            return float(value)
        except (ValueError, TypeError):
            return None


if __name__ == "__main__":
    try:
        KHANBANK_URI = os.getenv("KHANBANK_URI")
        if not KHANBANK_URI:
            raise ValueError("KHANBANK_URI not set in environment variables")

        today = datetime.date.today().isoformat()
        logger.info(f"Testing Khan Bank crawler for date: {today}")

        crawler = KhanBankCrawler(KHANBANK_URI, today)
        rates = crawler.crawl()

        if not rates:
            logger.warning("No rates fetched from Khan Bank")
        else:
            print(f"\n{'='*60}")
            print(f"Khan Bank Exchange Rates - {today}")
            print(f"{'='*60}\n")

            for code, detail in rates.items():
                print(f"{code.upper()}:")
                print(f"  Cash:    Buy: {detail.cash.buy:>10}  Sell: {detail.cash.sell:>10}")
                print(f"  Noncash: Buy: {detail.noncash.buy:>10}  Sell: {detail.noncash.sell:>10}")
                print()

            print(f"{'='*60}")
            print(f"Total currencies: {len(rates)}")
            print(f"{'='*60}\n")

    except Exception as e:
        logger.error(f"Error during test execution: {e}")
        raise
