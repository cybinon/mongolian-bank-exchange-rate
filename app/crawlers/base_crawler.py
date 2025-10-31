"""
Standard crawler template for Mongolian bank exchange rates.

All crawlers should follow this structure for consistency.
"""

import os
import urllib3
from abc import ABC, abstractmethod
from typing import Dict, Optional

from dotenv import load_dotenv

from app.config import config
from app.models.exchange_rate import CurrencyDetail, Rate
from app.utils.logger import get_logger

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = get_logger(__name__)


class BaseCrawler(ABC):
    """Base class for all bank crawlers."""

    BANK_NAME: str = "BaseBank"  # Override in subclasses

    def __init__(self, url: str, date: str):
        """
        Initialize the crawler.

        Args:
            url: Bank website/API URL
            date: Date in YYYY-MM-DD format
        """
        self.url = url
        self.date = date
        self.ssl_verify = config.SSL_VERIFY
        self.timeout = config.REQUEST_TIMEOUT

    @abstractmethod
    def crawl(self) -> Dict[str, CurrencyDetail]:
        """
        Collect exchange rates from the bank.

        Returns:
            Mapping: currency code (lowercase) -> CurrencyDetail

        Raises:
            TimeoutError: If the request times out
            RequestException: If the request fails
            ValueError: If the response format is invalid
        """
        pass

    @abstractmethod
    def _parse_rates(self, data) -> Dict[str, CurrencyDetail]:
        """
        Parse exchange rate data.

        Args:
            data: Raw data from API/webpage

        Returns:
            Dictionary mapping currency codes to CurrencyDetail objects
        """
        pass

    def _parse_float(self, value) -> Optional[float]:
        """
        Parse a value to float, handling various formats.

        Args:
            value: Value to parse (string, int, float, or None)

        Returns:
            Parsed float value or None if invalid
        """
        if not value:
            return None
        try:
            if isinstance(value, (int, float)):
                return float(value) if value != 0 else None

            cleaned = str(value).strip().replace(",", "").replace(" ", "").replace("\xa0", "")
            if not cleaned or cleaned == "-" or cleaned == "0":
                return None
            return float(cleaned)
        except (ValueError, TypeError, AttributeError):
            return None

    def _log_success(self, rates: Dict[str, CurrencyDetail]):
        """Log successful crawl."""
        logger.info(f"Successfully fetched {len(rates)} currencies from {self.BANK_NAME}")

    def _log_error(self, error: Exception, context: str = ""):
        """Log error with context."""
        error_msg = f"Error in {self.BANK_NAME}"
        if context:
            error_msg += f" ({context})"
        error_msg += f": {error}"
        logger.error(error_msg)


# Example implementation:
"""
class ExampleBankCrawler(BaseCrawler):
    BANK_NAME = "ExampleBank"
    
    def crawl(self) -> Dict[str, CurrencyDetail]:
        logger.info(f"Fetching rates from {self.BANK_NAME}: {self.url}")
        
        try:
            # Fetch data
            response = requests.get(self.url, verify=self.ssl_verify, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            # Parse data
            rates = self._parse_rates(data)
            self._log_success(rates)
            return rates
            
        except Exception as e:
            self._log_error(e)
            raise
    
    def _parse_rates(self, data: list) -> Dict[str, CurrencyDetail]:
        rates = {}
        for item in data:
            try:
                currency_code = item['code'].strip().lower()
                rates[currency_code] = CurrencyDetail(
                    cash=Rate(
                        buy=self._parse_float(item.get('cash_buy')),
                        sell=self._parse_float(item.get('cash_sell'))
                    ),
                    noncash=Rate(
                        buy=self._parse_float(item.get('noncash_buy')),
                        sell=self._parse_float(item.get('noncash_sell'))
                    )
                )
            except (KeyError, ValueError) as e:
                logger.warning(f"Error parsing {item.get('code', 'unknown')}: {e}")
                continue
        return rates
"""
