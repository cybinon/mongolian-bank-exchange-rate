"""
Crawler for Golomt Bank exchange rates.
"""
import requests
import datetime
from dotenv import load_dotenv
import os
import urllib3
from typing import Dict, Optional

load_dotenv()

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from app.models.exchange_rate import Rate, CurrencyDetail
from app.utils.logger import get_logger

logger = get_logger(__name__)

class GolomtBankCrawler:
    """Crawler to fetch exchange rates from Golomt Bank API."""
    BANK_NAME = "GolomtBank"
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
        self.ssl_verify = os.getenv("SSL_VERIFY", "True").lower() in ('true', '1', 't')

    def crawl(self) -> Dict[str, CurrencyDetail]:
        """
        Fetch exchange rates from Golomt Bank API.

        Returns:
            Mapping of currency code -> CurrencyDetail
        """
        date_formatted = self.date.replace("-", "")
        endpoint = f"{self.url}?date={date_formatted}"
        logger.info(f"Fetching rates from {self.BANK_NAME}: {endpoint}")
        
        try:
            response = requests.get(
                url=endpoint,
                verify=self.ssl_verify,
                timeout=self.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            data = response.json()
            
            if not isinstance(data, dict) or 'result' not in data:
                raise ValueError(f"Expected dict with 'result' key, got {type(data)}")
            
            rates = self._parse_rates(data['result'])
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
    
    def _parse_rates(self, data: dict) -> Dict[str, CurrencyDetail]:
        rates = {}
        
        for currency_code, currency_data in data.items():
            if not isinstance(currency_data, dict):
                logger.warning(f"Skipping {currency_code}: invalid data format")
                continue

            try:
                # Extract cash and non-cash rates
                cash_buy = currency_data.get("cash_buy", {})
                cash_sell = currency_data.get("cash_sell", {})
                non_cash_buy = currency_data.get("non_cash_buy", {})
                non_cash_sell = currency_data.get("non_cash_sell", {})
                
                rates[currency_code.lower()] = CurrencyDetail(
                    cash=Rate(
                        buy=self._parse_rate_value(cash_buy.get("cvalue")),
                        sell=self._parse_rate_value(cash_sell.get("cvalue"))
                    ),
                    noncash=Rate(
                        buy=self._parse_rate_value(non_cash_buy.get("cvalue")),
                        sell=self._parse_rate_value(non_cash_sell.get("cvalue"))
                    )
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
        GOLOMT_URI = os.getenv("GOLOMT_URI")
        if not GOLOMT_URI:
            raise ValueError("GOLOMT_URI not set in environment variables")
        
        today = datetime.date.today().isoformat()
        logger.info(f"Testing Golomt Bank crawler for date: {today}")
        
        crawler = GolomtBankCrawler(GOLOMT_URI, today)
        rates = crawler.crawl()

        if not rates:
            logger.warning("No rates fetched from Golomt Bank")
        else:
            print(f"\n{'='*60}")
            print(f"Golomt Bank Exchange Rates - {today}")
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
