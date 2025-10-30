"""
Худалдаа Хөгжлийн Банкны валютын ханш цуглуулагч (Playwright ашиглан).
"""
import os
import urllib3
from typing import Dict, Optional
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from datetime import datetime, timedelta
import time

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from app.models.exchange_rate import Rate, CurrencyDetail
from app.utils.logger import get_logger

logger = get_logger(__name__)

class TDBMCrawler:
    """ТХАБ-ын вэбсайтаас валютын ханш татах цуглуулагч."""
    BANK_NAME = "TDBM"
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
        ТХАБ-ын вэбсайтаас валютын ханш татах.
        
        Returns:
            Валютын код -> CurrencyDetail объектын толь
        """
        logger.info(f"Fetching rates from {self.BANK_NAME}: {self.url}")
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(ignore_https_errors=not self.ssl_verify)
                page = context.new_page()
                
                page.goto(self.url, timeout=self.REQUEST_TIMEOUT, wait_until='networkidle')
                page.wait_for_selector('table.table-hover', timeout=self.REQUEST_TIMEOUT)
                
                # Find and set date to yesterday if today has no data
                date_inputs = page.locator('input[type=date]').all()
                if date_inputs:
                    # Try today first
                    today = datetime.now().strftime('%Y-%m-%d')
                    date_inputs[0].fill(today)
                    
                    # Click submit button to load data
                    buttons = page.locator('form button, form input[type=submit]').all()
                    if buttons:
                        buttons[0].click()
                        time.sleep(3)
                    
                    # Check if we have data
                    rates = self._parse_rates(page)
                    
                    # If no rates, try yesterday
                    if not rates:
                        logger.info(f"{self.BANK_NAME} has no data for today, trying yesterday")
                        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
                        date_inputs[0].fill(yesterday)
                        if buttons:
                            buttons[0].click()
                            time.sleep(3)
                        rates = self._parse_rates(page)
                else:
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
        
        rows = page.locator('table.table-hover tbody tr').all()
        
        for row in rows:
            cells = row.locator('td').all()
            
            if len(cells) >= 7:
                try:
                    currency_code = cells[1].inner_text().strip().lower()
                    
                    if not currency_code or len(currency_code) != 3:
                        continue
                    
                    mongol_bank = self._parse_float(cells[3].inner_text())
                    noncash_buy = self._parse_float(cells[4].inner_text())
                    noncash_sell = self._parse_float(cells[5].inner_text())
                    cash_buy = self._parse_float(cells[6].inner_text())
                    cash_sell = self._parse_float(cells[7].inner_text())
                    
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
    url = os.getenv("TDBM_URI", "https://www.tdbm.mn/en/exchange")
    crawler = TDBMCrawler(url=url, date="")
    try:
        rates = crawler.crawl()
        if len(rates) == 0:
            print(f"TDBM has no rates available")
        else:
            print(f"Successfully fetched rates for {len(rates)} currencies")
            for currency, details in rates.items():
                print(f"{currency.upper()}: Cash Buy={details.cash.buy}, Cash Sell={details.cash.sell}, "
                      f"Non-Cash Buy={details.noncash.buy}, Non-Cash Sell={details.noncash.sell}")
    except Exception as e:
        print(f"Error: {e}")
