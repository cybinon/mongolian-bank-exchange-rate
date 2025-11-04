"""
Service module to collect exchange rates from multiple banks.
"""

import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Tuple

from app.config import config
from app.crawlers.arigbank import ArigBankCrawler
from app.crawlers.bogdbank import BogdBankCrawler
from app.crawlers.capitronbank import CapitronBankCrawler
from app.crawlers.ckbank import CKBankCrawler
from app.crawlers.golomt import GolomtBankCrawler
from app.crawlers.khanbank import KhanBankCrawler
from app.crawlers.mbank import MBankCrawler
from app.crawlers.mongolbank import MongolBankCrawler
from app.crawlers.nibank import NIBankCrawler
from app.crawlers.statebank import StateBankCrawler
from app.crawlers.tdbm import TDBMCrawler
from app.crawlers.transbank import TransBankCrawler
from app.crawlers.xacbank import XacBankCrawler
from app.db import repository
from app.db.database import SessionLocal
from app.models.exchange_rate import CurrencyDetail, ExchangeRate
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ScraperService:
    """Service for scraping exchange rates from multiple banks."""

    def __init__(self, date: Optional[str] = None):
        """
        Initialize the scraper service.

        Args:
            date: Date in ISO format (YYYY-MM-DD). Defaults to today.
        """
        self.date = date or datetime.date.today().isoformat()
        self.crawlers = [
            KhanBankCrawler(config.KHANBANK_URI, self.date),
            GolomtBankCrawler(config.GOLOMT_URI, self.date),
            MongolBankCrawler(config.MONGOLBANK_URI, self.date),
            TDBMCrawler(config.TDBM_URI, self.date),
            XacBankCrawler(config.XACBANK_URI, self.date),
            ArigBankCrawler(config.ARIGBANK_URI, self.date),
            BogdBankCrawler(config.BOGDBANK_URI, self.date),
            StateBankCrawler(config.STATEBANK_URI, self.date),
            CapitronBankCrawler(config.CAPITRONBANK_URI, self.date),
            TransBankCrawler(config.TRANSBANK_URI, self.date),
            NIBankCrawler(config.NIBANK_URI, self.date),
            MBankCrawler(config.MBANK_URI, self.date),
            CKBankCrawler(config.CKBANK_URI, self.date),
        ]

    def run_crawlers(self):
        def _crawl_one(crawler) -> Tuple[str, Optional[Dict[str, CurrencyDetail]], Optional[Exception]]:
            bank_name = crawler.__class__.__name__.replace("Crawler", "")
            try:
                rates = crawler.crawl()
                return bank_name, rates, None
            except Exception as e:
                return bank_name, None, e

        results: List[Tuple[str, Optional[Dict[str, CurrencyDetail]], Optional[Exception]]] = []

        if config.ENABLE_PARALLEL:
            logger.info(
                f"Running crawlers in parallel for date {self.date}: http={len(http_crawlers)} (max={config.MAX_WORKERS}), browser={len(playwright_crawlers)} (max={config.PLAYWRIGHT_MAX_WORKERS})"
            )
            # Run both pools concurrently
            with ThreadPoolExecutor(max_workers=2) as coordinator:
                http_future = coordinator.submit(self._run_pool, http_crawlers, _crawl_one, config.MAX_WORKERS)
                pw_future = coordinator.submit(
                    self._run_pool, playwright_crawlers, _crawl_one, config.PLAYWRIGHT_MAX_WORKERS
                )
                for future in as_completed([http_future, pw_future]):
                    results.extend(future.result())
        else:
            logger.info(f"Running crawlers sequentially for date {self.date}")
            for crawler in self.crawlers:
                bank_name, rates, error = _crawl_one(crawler)
                if error:
                    logger.error(f"Failed to crawl from {bank_name}: {error}")
                else:
                    logger.info(f"Successfully crawled {bank_name} with {len(rates or {})} currencies")
                results.append((bank_name, rates, error))

        db = SessionLocal()
        try:
            for bank_name, rates, error in results:
                if error or not rates:
                    continue
                try:
                    exchange_rate_data = ExchangeRate(date=self.date, bank=bank_name, rates=rates)
                    repository.save_rates(db, exchange_rate_data)
                    logger.info(f"Saved rates from {bank_name}")
                except Exception as e:
                    logger.error(f"Failed to save rates for {bank_name}: {e}")
        finally:
            db.close()

    @staticmethod
    def _run_pool(crawlers: List[object], worker, max_workers: int):
        results: List[Tuple[str, Optional[Dict[str, CurrencyDetail]], Optional[Exception]]] = []
        if not crawlers or max_workers <= 0:
            return results
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_map = {executor.submit(worker, crawler): crawler for crawler in crawlers}
            for future in as_completed(future_map):
                bank_name, rates, error = future.result()
                if error:
                    logger.error(f"Failed to crawl from {bank_name}: {error}")
                else:
                    logger.info(f"Successfully crawled {bank_name} with {len(rates or {})} currencies")
                results.append((bank_name, rates, error))
        return results

    def scrape_bank(self, bank_name: str) -> Optional[Dict[str, CurrencyDetail]]:
        """
        Scrape a specific bank without saving to the database.

        Args:
            bank_name: Bank name (case-insensitive)

        Returns:
            Dict of currency rates, or None if bank not found
        """
        bank_name_lower = bank_name.lower()

        crawler_map = {
            "khanbank": lambda: KhanBankCrawler(config.KHANBANK_URI, self.date),
            "golomt": lambda: GolomtBankCrawler(config.GOLOMT_URI, self.date),
            "golomtbank": lambda: GolomtBankCrawler(config.GOLOMT_URI, self.date),
            "mongolbank": lambda: MongolBankCrawler(config.MONGOLBANK_URI, self.date),
            "tdbm": lambda: TDBMCrawler(config.TDBM_URI, self.date),
            "xacbank": lambda: XacBankCrawler(config.XACBANK_URI, self.date),
            "arigbank": lambda: ArigBankCrawler(config.ARIGBANK_URI, self.date),
            "bogdbank": lambda: BogdBankCrawler(config.BOGDBANK_URI, self.date),
            "statebank": lambda: StateBankCrawler(config.STATEBANK_URI, self.date),
            "capitronbank": lambda: CapitronBankCrawler(config.CAPITRONBANK_URI, self.date),
            "transbank": lambda: TransBankCrawler(config.TRANSBANK_URI, self.date),
            "nibank": lambda: NIBankCrawler(config.NIBANK_URI, self.date),
            "mbank": lambda: MBankCrawler(config.MBANK_URI, self.date),
            "ckbank": lambda: CKBankCrawler(config.CKBANK_URI, self.date),
        }

        crawler_factory = crawler_map.get(bank_name_lower)
        if not crawler_factory:
            logger.error(f"Bank not found: {bank_name}")
            return None

        try:
            crawler = crawler_factory()
            rates = crawler.crawl()
            logger.info(f"Successfully scraped rates from {bank_name}")
            return rates
        except Exception as e:
            logger.error(f"Failed to scrape from {bank_name}: {e}")
            return None
