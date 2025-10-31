"""
Crawler for XacBank exchange rates.
"""
import requests
import os
import urllib3
from typing import Dict, Optional
from dotenv import load_dotenv
from datetime import datetime, timedelta
from urllib.parse import quote

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from app.models.exchange_rate import Rate, CurrencyDetail
from app.utils.logger import get_logger

logger = get_logger(__name__)

class XacBankCrawler:
    """Crawler to fetch exchange rates from XacBank API."""
    BANK_NAME = "XacBank"
    REQUEST_TIMEOUT = 30
    BASE_API_URL = "https://xacbank.mn/api/currencies"
    
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
        Fetch exchange rates from XacBank API.

        Returns:
            Mapping of currency code -> CurrencyDetail
        """
        logger.info(f"Fetching rates from {self.BANK_NAME}: {self.BASE_API_URL}")
        
        try:
            if self.date:
                target_date = datetime.strptime(self.date, '%Y-%m-%d')
            else:
                target_date = datetime.now() - timedelta(days=1)
            
            api_url = self._build_api_url(target_date)
            
            response = requests.get(
                url=api_url,
                verify=self.ssl_verify,
                timeout=self.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            data = response.json()
            
            if not data.get('docs') or len(data['docs']) == 0:
                logger.info(f"{self.BANK_NAME} has no data for {target_date.strftime('%Y-%m-%d')}, trying previous day")
                yesterday = target_date - timedelta(days=1)
                api_url = self._build_api_url(yesterday)
                
                response = requests.get(
                    url=api_url,
                    verify=self.ssl_verify,
                    timeout=self.REQUEST_TIMEOUT
                )
                response.raise_for_status()
                data = response.json()
            
            rates = self._parse_rates(data.get('docs', []))
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
    
    def _build_api_url(self, date: datetime) -> str:
        start_utc = date.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(hours=8)
        end_utc = date.replace(hour=23, minute=59, second=59, microsecond=999000) - timedelta(hours=8)
        
        start_str = start_utc.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        end_str = end_utc.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        
        url = f"{self.BASE_API_URL}?sort=position"
        url += f"&where%5Bdate%5D%5Bgreater_than_equal%5D={quote(start_str)}"
        url += f"&where%5Bdate%5D%5Bless_than%5D={quote(end_str)}"
        url += "&pagination=false"
        
        return url
    
    def _parse_rates(self, docs: list) -> Dict[str, CurrencyDetail]:
        rates = {}
        
        for item in docs:
            currency_code = item.get('code', '').lower()
            
            if not currency_code:
                continue
            
            buy_cash = item.get('buyCash', 0)
            sell_cash = item.get('sellCash', 0)
            buy_noncash = item.get('buy', 0)
            sell_noncash = item.get('sell', 0)
            
            rates[currency_code] = CurrencyDetail(
                cash=Rate(
                    buy=float(buy_cash) if buy_cash else 0.0,
                    sell=float(sell_cash) if sell_cash else 0.0
                ),
                noncash=Rate(
                    buy=float(buy_noncash) if buy_noncash else 0.0,
                    sell=float(sell_noncash) if sell_noncash else 0.0
                )
            )
        
        return rates

if __name__ == "__main__":
    url = os.getenv("XACBANK_URI", "https://xacbank.mn/calculator/rates?lang=en")
    crawler = XacBankCrawler(url=url, date="")
    try:
        rates = crawler.crawl()
        print(f"Successfully fetched rates for {len(rates)} currencies")
        for currency, details in rates.items():
            print(f"{currency.upper()}: Cash Buy={details.cash.buy}, Cash Sell={details.cash.sell}, "
                  f"Non-Cash Buy={details.noncash.buy}, Non-Cash Sell={details.noncash.sell}")
    except Exception as e:
        print(f"Error: {e}")