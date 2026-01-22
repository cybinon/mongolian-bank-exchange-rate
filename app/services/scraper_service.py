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

logger = get_logger("scraper")


class ScraperService:
    def __init__(self, date: Optional[str] = None):
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
        logger.info(f"Starting crawl for {len(self.crawlers)} banks on {self.date}")
        crawlers_map = self._group_crawlers()
        results = []

        if config.ENABLE_PARALLEL:
            with ThreadPoolExecutor(max_workers=2) as coordinator:
                futures = [
                    coordinator.submit(
                        self._run_crawler_group,
                        group,
                        config.MAX_WORKERS if type_ == "http" else config.PLAYWRIGHT_MAX_WORKERS,
                    )
                    for type_, group in crawlers_map.items()
                ]
                for future in as_completed(futures):
                    results.extend(future.result())
        else:
            for crawler in self.crawlers:
                results.append(self._execute_crawler(crawler))

        self._save_results(results)
        logger.info(
            f"Crawl completed: {len([r for r in results if r[1]])} succeeded, {len([r for r in results if r[2]])} failed"
        )

    def _group_crawlers(self) -> Dict[str, List]:
        playwright_classes = (
            TDBMCrawler,
            TransBankCrawler,
            NIBankCrawler,
            MBankCrawler,
            BogdBankCrawler,
            CKBankCrawler,
        )
        return {
            "playwright": [c for c in self.crawlers if isinstance(c, playwright_classes)],
            "http": [c for c in self.crawlers if not isinstance(c, playwright_classes)],
        }

    def _run_crawler_group(
        self, crawlers: List, max_workers: int
    ) -> List[Tuple[str, Optional[Dict], Optional[Exception]]]:
        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_crawler = {executor.submit(self._execute_crawler, c): c for c in crawlers}
            for future in as_completed(future_to_crawler):
                results.append(future.result())
        return results

    def _execute_crawler(self, crawler) -> Tuple[str, Optional[Dict], Optional[Exception]]:
        bank_name = crawler.__class__.__name__.replace("Crawler", "")
        try:
            rates = crawler.crawl()
            logger.info(f"{bank_name}: crawled {len(rates) if rates else 0} currencies")
            return bank_name, rates, None
        except Exception as e:
            logger.exception(f"{bank_name}: crawl failed - {e}")
            return bank_name, None, e

    def _save_results(self, results):
        db = SessionLocal()
        saved_count = 0
        try:
            for bank_name, rates, error in results:
                if error or not rates:
                    continue
                try:
                    exchange_rate_data = ExchangeRate(date=self.date, bank=bank_name, rates=rates)
                    repository.save_rates(db, exchange_rate_data)
                    saved_count += 1
                except Exception as e:
                    logger.exception(f"{bank_name}: failed to save rates - {e}")
        finally:
            db.close()
            logger.info(f"Saved {saved_count} bank rates to database")

    def scrape_bank(self, bank_name: str) -> Optional[Dict[str, CurrencyDetail]]:
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
            logger.warning(f"Unknown bank: {bank_name}")
            return None

        try:
            crawler = crawler_factory()
            rates = crawler.crawl()
            logger.info(f"{bank_name}: scraped {len(rates) if rates else 0} currencies")
            return rates
        except Exception as e:
            logger.exception(f"{bank_name}: scrape failed - {e}")
            return None
