"""
Exchange rate crawler for NIBank (using Playwright).
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

class NIBankCrawler:
    """Crawler for fetching exchange rates from NIBank's website."""
    BANK_NAME = "NIBank"
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
        self.ssl_verify = os.getenv("SSL_VERIFY", "True").lower() in ('true', '1', 't')

    def crawl(self) -> Dict[str, CurrencyDetail]:
        """
        Fetch exchange rates from NIBank.
        
        Returns:
            Dict mapping currency code -> CurrencyDetail object
        """
        logger.info(f"Fetching rates from {self.BANK_NAME}: {self.url}")
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                page.goto(self.url, timeout=self.REQUEST_TIMEOUT, wait_until='networkidle')
                
                # Wait for exchange rate blocks to load
                page.wait_for_selector('.exchange-block', timeout=self.REQUEST_TIMEOUT)
                
                rates = self._parse_exchange_blocks(page)
                
                browser.close()
                
                logger.info(f"Successfully fetched {len(rates)} currencies from {self.BANK_NAME}")
                return rates
                
        except TimeoutError:
            logger.error(f"Timeout while fetching from {self.BANK_NAME}")
            raise
        except Exception as e:
            logger.error(f"Error while crawling {self.BANK_NAME}: {e}")
            raise

    def _parse_exchange_blocks(self, page) -> Dict[str, CurrencyDetail]:
        rates = {}
        
        try:
            # Find all exchange blocks
            blocks = page.locator('.exchange-block').all()
            
            for block in blocks:
                try:
                    text = block.inner_text()
                    lines = [line.strip() for line in text.split('\n') if line.strip()]
                    
                    if len(lines) < 6:
                        continue
                    
                    # Extract currency code from first line (e.g., "USD ($)" -> "usd")
                    currency_line = lines[0]
                    currency_match = re.match(r'^([A-Z]{3})', currency_line)
                    if not currency_match:
                        continue
                    
                    currency_code = currency_match.group(1).lower()
                    
                    # Parse rates based on labels
                    cash_buy = None
                    cash_sell = None
                    noncash_buy = None
                    noncash_sell = None
                    
                    for i, line in enumerate(lines):
                        if 'Бэлэн авах' in line and i + 1 < len(lines):
                            cash_buy = self._parse_float(lines[i + 1])
                        elif 'Бэлэн зарах' in line and i + 1 < len(lines):
                            cash_sell = self._parse_float(lines[i + 1])
                        elif 'Бэлэн бус авах' in line and i + 1 < len(lines):
                            noncash_buy = self._parse_float(lines[i + 1])
                        elif 'Бэлэн бус за' in line and i + 1 < len(lines):
                            noncash_sell = self._parse_float(lines[i + 1])
                    
                    rates[currency_code] = CurrencyDetail(
                        cash=Rate(buy=cash_buy, sell=cash_sell),
                        noncash=Rate(buy=noncash_buy, sell=noncash_sell)
                    )
                    
                except Exception as e:
                    logger.warning(f"Error parsing exchange block: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error parsing exchange blocks: {e}")
            raise
        
        return rates
    
    def _parse_float(self, value) -> float:
        try:
            if isinstance(value, (int, float)):
                return float(value) if value != 0 else None
            
            cleaned = str(value).strip().replace(',', '').replace(' ', '').replace('\xa0', '')
            if not cleaned or cleaned == '-' or cleaned == '0':
                return None
            return float(cleaned)
        except (ValueError, TypeError):
            return None
