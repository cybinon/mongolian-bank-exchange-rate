"""
Crawler for MongolBank exchange rates.
"""
import requests
import os
import urllib3
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from app.models.exchange_rate import Rate, CurrencyDetail
from app.utils.logger import get_logger

logger = get_logger(__name__)

class MongolBankCrawler:
    """Crawler to fetch exchange rates from MongolBank API."""
    BANK_NAME = "MongolBank"
    REQUEST_TIMEOUT = 30
    API_URL = "https://www.mongolbank.mn/en/currency-rate-movement/data"
    
    def __init__(self, url: str, date: str):
        """
        Initialize the crawler.

        Args:
            url: Bank website/API URL
            date: Date in YYYY-MM-DD format
        """
        self.url = url
        self.date = date
        self.ssl_verify = os.getenv("SSL_VERIFY", "True").lower() in ('true', '1', 't')

    def crawl(self) -> Dict[str, CurrencyDetail]:
        """
        Fetch exchange rates from MongolBank API.

        Returns:
            Mapping of currency code -> CurrencyDetail
        """
        logger.info(f"Fetching rates from {self.BANK_NAME}: {self.API_URL}")
        
        try:
            response = requests.post(
                url=self.API_URL,
                verify=self.ssl_verify,
                timeout=self.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            json_data = response.json()
            
            if not json_data.get('success'):
                raise ValueError("API returned success=false")
            
            data = json_data.get('data', [])
            if not isinstance(data, list) or len(data) == 0:
                raise ValueError(f"Expected non-empty list in data field")
            
            rates = self._parse_rates(data[0])
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
        
        for key, value in data.items():
            if key == 'RATE_DATE':
                continue
                
            if value and value != '-':
                currency_code = key.lower()
                rate_value = self._parse_rate_value(value)
                
                if rate_value is not None:
                    rates[currency_code] = CurrencyDetail(
                        cash=Rate(buy=rate_value, sell=rate_value),
                        noncash=Rate(buy=rate_value, sell=rate_value)
                    )
        
        return rates
    
    def _parse_rate_value(self, value: Optional[str]) -> Optional[float]:
        if not value:
            return None
        try:
            cleaned = value.replace(',', '').strip()
            return float(cleaned)
        except (ValueError, AttributeError):
            return None

if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    
    from datetime import date
    
    url = os.getenv("MONGOLBANK_URI")
    today = date.today().isoformat()
    
    crawler = MongolBankCrawler(url=url, date=today)
    try:
        rates = crawler.crawl()
        print(f"Successfully fetched rates for {len(rates)} currencies")
        for currency, detail in rates.items():
            print(f"{currency.upper()}: {detail.noncash.buy}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
