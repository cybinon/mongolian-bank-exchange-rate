"""
Crawler for Capitron Bank exchange rates.
"""

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


class CapitronBankCrawler:
    """Crawler to fetch exchange rates from Capitron Bank API."""

    BANK_NAME = "CapitronBank"
    REQUEST_TIMEOUT = 30
    API_URL = "https://www.capitronbank.mn/admin/en/wp-json/bank/rates/capitronbank"

    def __init__(self, url: str, date: str):
        """
        Initialize the crawler.

        Args:
            url: Bank website/API URL
            date: Date in YYYY-MM-DD format
        """
        self.url = url
        self.date = date
        self.ssl_verify = os.getenv("SSL_VERIFY", "True").lower() in ("true", "1", "t")

    def crawl(self) -> Dict[str, CurrencyDetail]:
        """
        Fetch exchange rates from Capitron Bank API.

        Returns:
            Mapping of currency code -> CurrencyDetail
        """
        logger.info(f"Fetching rates from {self.BANK_NAME}: {self.API_URL}")

        try:
            response = requests.get(url=self.API_URL, verify=self.ssl_verify, timeout=self.REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()

            if not isinstance(data, list):
                raise ValueError(f"Expected list, got {type(data)}")

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
            currency_code = item.get("curcode", "").lower()
            rtypecode = item.get("rtypecode", "")

            if not currency_code or currency_code == "mnt":
                continue

            if currency_code not in rates:
                rates[currency_code] = CurrencyDetail(cash=Rate(buy=0.0, sell=0.0), noncash=Rate(buy=0.0, sell=0.0))

            buy_rate = self._parse_float(item.get("buyrate", "0"))
            sell_rate = self._parse_float(item.get("salerate", "0"))

            if rtypecode == "1":
                rates[currency_code].cash.buy = buy_rate if buy_rate else 0.0
                rates[currency_code].cash.sell = sell_rate if sell_rate else 0.0
            elif rtypecode == "2":
                rates[currency_code].noncash.buy = buy_rate if buy_rate else 0.0
                rates[currency_code].noncash.sell = sell_rate if sell_rate else 0.0

        return rates

    def _parse_float(self, value) -> Optional[float]:
        if not value:
            return None
        try:
            if isinstance(value, str):
                cleaned = value.replace(",", "").strip()
                return float(cleaned)
            return float(value)
        except (ValueError, AttributeError):
            return None


if __name__ == "__main__":
    import sys

    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

    from datetime import date

    url = os.getenv("CAPITRONBANK_URI", "https://www.capitronbank.mn/p/exchange?lang=en")

    today = date.today().isoformat()
    print(f"\n{'='*60}")
    print(f"Testing CapitronBank crawler for today: {today}")
    print(f"{'='*60}\n")

    crawler = CapitronBankCrawler(url=url, date=today)
    try:
        rates = crawler.crawl()
        if len(rates) == 0:
            print(f"CapitronBank has no rates available for {today}")
        else:
            print(f"Successfully fetched rates for {len(rates)} currencies")
            for currency, details in list(rates.items())[:3]:
                print(
                    f"{currency.upper()}: Cash Buy={details.cash.buy}, Cash Sell={details.cash.sell}, "
                    f"Non-Cash Buy={details.noncash.buy}, Non-Cash Sell={details.noncash.sell}"
                )
    except Exception as e:
        print(f"Error: {e}")
