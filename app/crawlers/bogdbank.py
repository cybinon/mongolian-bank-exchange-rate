"""
Богд банкны валютын ханш цуглуулагч (Playwright ашиглан).
"""
import os
import urllib3
from typing import Dict, Optional
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import time

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from app.models.exchange_rate import Rate, CurrencyDetail
from app.utils.logger import get_logger

logger = get_logger(__name__)

class BogdBankCrawler:
    """Богд банкны вэбсайтаас валютын ханш татах цуглуулагч."""
    BANK_NAME = "BogdBank"
    REQUEST_TIMEOUT = 60000
    
    def __init__(self, url: str, date: str):
        """
        Цуглуулагчийг эхлүүлэх.
        
        Args:
            url: Банкны вэбсайтын URL
            date: Огноо YYYY-MM-DD форматаар
        """
        self.url = url
        self.date = date
        self.ssl_verify = os.getenv("SSL_VERIFY", "True").lower() in ('true', '1', 't')

    def crawl(self) -> Dict[str, CurrencyDetail]:
        """
        Богд банкны вэбсайтаас валютын ханш татах.
        
        Returns:
            Валютын код -> CurrencyDetail объектын толь
        """
        logger.info(f"Fetching rates from {self.BANK_NAME}: {self.url}")
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(ignore_https_errors=not self.ssl_verify)
                page = context.new_page()
                
                url_with_date = f"{self.url}?date={self.date}" if self.date else self.url
                
                page.goto(url_with_date, timeout=self.REQUEST_TIMEOUT, wait_until='networkidle')
                page.wait_for_selector('table', timeout=self.REQUEST_TIMEOUT)
                time.sleep(2)
                
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
        
        rows = page.locator('table tbody tr').all()
        
        for row in rows:
            cells = row.locator('td').all()
            
            if len(cells) >= 6:
                try:
                    currency_text = cells[0].inner_text().strip()
                    currency_code = currency_text.replace('\xa0', '').replace(' ', '').lower()
                    
                    if not currency_code or len(currency_code) < 3:
                        continue
                    
                    cash_buy = self._parse_float(cells[2].inner_text())
                    cash_sell = self._parse_float(cells[3].inner_text())
                    noncash_buy = self._parse_float(cells[4].inner_text())
                    noncash_sell = self._parse_float(cells[5].inner_text())
                    
                    rates[currency_code] = CurrencyDetail(
                        cash=Rate(
                            buy=cash_buy if cash_buy else 0.0,
                            sell=cash_sell if cash_sell else 0.0
                        ),
                        noncash=Rate(
                            buy=noncash_buy if noncash_buy else 0.0,
                            sell=noncash_sell if noncash_sell else 0.0
                        )
                    )
                except Exception as e:
                    logger.debug(f"Skipping row due to parsing error: {e}")
                    continue
        
        return rates
    
    def _parse_float(self, value: str) -> Optional[float]:
        if not value or value == '-' or value.strip() == '':
            return None
        try:
            cleaned = value.replace(',', '').strip()
            return float(cleaned)
        except ValueError:
            return None

if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    
    from datetime import date, timedelta
    
    url = os.getenv("BOGDBANK_URI", "https://www.bogdbank.com/exchange")
    
    today = date.today().isoformat()
    print(f"\n{'='*60}")
    print(f"Testing BogdBank crawler for today: {today}")
    print(f"{'='*60}\n")
    
    crawler = BogdBankCrawler(url=url, date=today)
    try:
        rates = crawler.crawl()
        if len(rates) == 0:
            print(f"BogdBank has no rates available for {today}")
        else:
            print(f"Successfully fetched rates for {len(rates)} currencies")
            for currency, details in list(rates.items())[:5]:
                print(f"{currency.upper()}: Cash Buy={details.cash.buy}, Cash Sell={details.cash.sell}, "
                      f"Non-Cash Buy={details.noncash.buy}, Non-Cash Sell={details.noncash.sell}")
    except Exception as e:
        print(f"Error: {e}")
    
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    print(f"\n{'='*60}")
    print(f"Testing BogdBank crawler for yesterday: {yesterday}")
    print(f"{'='*60}\n")
    
    crawler2 = BogdBankCrawler(url=url, date=yesterday)
    try:
        rates2 = crawler2.crawl()
        if len(rates2) == 0:
            print(f"BogdBank has no rates available for {yesterday}")
        else:
            print(f"Successfully fetched rates for {len(rates2)} currencies")
            for currency, details in list(rates2.items())[:5]:
                print(f"{currency.upper()}: Cash Buy={details.cash.buy}, Cash Sell={details.cash.sell}, "
                      f"Non-Cash Buy={details.noncash.buy}, Non-Cash Sell={details.noncash.sell}")
    except Exception as e:
        print(f"Error: {e}")
