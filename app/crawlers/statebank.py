"""
Crawler for State Bank exchange rates.
"""

import os
from typing import Dict

import requests
import urllib3
from dotenv import load_dotenv

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from app.models.exchange_rate import CurrencyDetail, Rate
from app.utils.logger import get_logger

logger = get_logger(__name__)


class StateBankCrawler:
    """Crawler to fetch exchange rates from State Bank API."""

    BANK_NAME = "StateBank"
    REQUEST_TIMEOUT = 30

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
        Fetch exchange rates from State Bank API.

        Returns:
            Mapping of currency code -> CurrencyDetail
        """
        logger.info(f"Fetching rates from {self.BANK_NAME}: {self.url}")

        try:
            response = requests.get(url=self.url, verify=self.ssl_verify, timeout=self.REQUEST_TIMEOUT)
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
            currency_code = item.get("curCode", "").lower()

            if not currency_code or currency_code == "mnt":
                continue

            cash_buy = item.get("cashBuy", 0)
            cash_sell = item.get("cashSale", 0)
            noncash_buy = item.get("nonCashBuy", 0)
            noncash_sell = item.get("nonCashSale", 0)

            if cash_buy or cash_sell or noncash_buy or noncash_sell:
                rates[currency_code] = CurrencyDetail(
                    cash=Rate(buy=float(cash_buy) if cash_buy else 0.0, sell=float(cash_sell) if cash_sell else 0.0),
                    noncash=Rate(
                        buy=float(noncash_buy) if noncash_buy else 0.0,
                        sell=float(noncash_sell) if noncash_sell else 0.0,
                    ),
                )

        return rates


if __name__ == "__main__":
    url = os.getenv("STATEBANK_URI", "https://www.statebank.mn/back/api/fetchrate")
    crawler = StateBankCrawler(url=url, date="")
    try:
        rates = crawler.crawl()
        print(f"Successfully fetched rates for {len(rates)} currencies")
        for currency, details in rates.items():
            print(
                f"{currency.upper()}: Cash Buy={details.cash.buy}, Cash Sell={details.cash.sell}, "
                f"Non-Cash Buy={details.noncash.buy}, Non-Cash Sell={details.noncash.sell}"
            )
    except Exception as e:
        print(f"Error: {e}")
