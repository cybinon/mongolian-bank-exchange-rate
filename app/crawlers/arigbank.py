"""
Crawler for Arig Bank exchange rates.
"""

from datetime import datetime
from typing import Dict

import requests
import urllib3
from dotenv import load_dotenv

from app.config import config
from app.models.exchange_rate import CurrencyDetail, Rate
from app.utils.logger import get_logger

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = get_logger(__name__)


class ArigBankCrawler:
    """Crawler to fetch exchange rates from Arig Bank API."""

    BANK_NAME = "ArigBank"

    def __init__(self, url: str, date: str):
        """
        Initialize Arig Bank crawler.

        Args:
            url: Bank website/API URL
            date: Date in YYYY-MM-DD format
        """
        self.url = url
        self.date = date
        self.API_URL = config.ARIGBANK_API_URL
        self.bearer_token = config.ARIGBANK_BEARER_TOKEN
        self.ssl_verify = config.SSL_VERIFY
        self.timeout = config.REQUEST_TIMEOUT

    def crawl(self) -> Dict[str, CurrencyDetail]:
        """
        Fetch exchange rates from Arig Bank API.

        Returns:
            Mapping of currency code -> CurrencyDetail
        """
        logger.info(f"Fetching rates from {self.BANK_NAME}: {self.API_URL}")

        try:
            date_str = self.date.replace("-", "")

            headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.bearer_token}"}

            payload = {"rateDate": date_str}

            response = requests.post(
                url=self.API_URL, headers=headers, json=payload, verify=self.ssl_verify, timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()
            data = result.get("data", [])

            if not isinstance(data, list):
                raise ValueError(f"Expected list in data field, got {type(data)}")

            rates = self._parse_rates(data)
            logger.info(f"Successfully fetched {len(rates)} currencies from {self.BANK_NAME}")
            return rates

        except requests.exceptions.Timeout:
            logger.error(f"Request timeout while fetching from {self.BANK_NAME}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {self.BANK_NAME}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while parsing {self.BANK_NAME} data: {e}")
            raise

    def _parse_rates(self, data: list) -> Dict[str, CurrencyDetail]:
        """
        Parse exchange rate data from API response.

        Args:
            data: List of currency rate dictionaries

        Returns:
            Dictionary mapping currency codes to CurrencyDetail objects
        """
        rates = {}
        for item in data:
            try:
                currency_code = item["curCode"].strip().lower()

                rates[currency_code] = CurrencyDetail(
                    cash=Rate(
                        buy=float(item["belenBuyRate"]) if item["belenBuyRate"] else None,
                        sell=float(item["belenSellRate"]) if item["belenSellRate"] else None,
                    ),
                    noncash=Rate(
                        buy=float(item["belenBusBuyRate"]) if item["belenBusBuyRate"] else None,
                        sell=float(item["belenBusSellRate"]) if item["belenBusSellRate"] else None,
                    ),
                )
            except (KeyError, ValueError) as e:
                logger.warning(f"Error parsing currency data for {item.get('curCode', 'unknown')}: {e}")
                continue

        return rates


if __name__ == "__main__":
    from datetime import timedelta

    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    for test_date in [today, yesterday]:
        logger.info(f"Fetching rates for {test_date}")
        crawler = ArigBankCrawler(config.ARIGBANK_URI, test_date)
        rates = crawler.crawl()
        logger.info(f"Found {len(rates)} currencies")

        for code, details in list(rates.items())[:3]:
            logger.info(
                f"{code.upper()}: Cash: Buy={details.cash.buy}, Sell={details.cash.sell}, "
                f"Non-Cash: Buy={details.noncash.buy}, Sell={details.noncash.sell}"
            )
