"""
Олон банкнаас мэдээлэл цуглуулах үйлчилгээний модуль.
"""
from app.crawlers.khanbank import KhanBankCrawler
from app.crawlers.tdbm import TDBMCrawler
from app.crawlers.golomt import GolomtBankCrawler
from app.crawlers.xacbank import XacBankCrawler
from app.crawlers.arigbank import ArigBankCrawler
from app.crawlers.bogdbank import BogdBankCrawler
from app.crawlers.statebank import StateBankCrawler
from app.crawlers.mongolbank import MongolBankCrawler
from app.crawlers.capitronbank import CapitronBankCrawler
from app.crawlers.transbank import TransBankCrawler
from app.crawlers.nibank import NIBankCrawler
from app.crawlers.mbank import MBankCrawler
from app.crawlers.ckbank import CKBankCrawler

from app.db import repository
from app.db.database import SessionLocal
from app.config import config
from app.utils.logger import get_logger
import datetime
from app.models.exchange_rate import ExchangeRate
from typing import Dict, Optional
from app.models.exchange_rate import CurrencyDetail

logger = get_logger(__name__)


class ScraperService:
    """Олон банкнаас валютын ханш цуглуулах үйлчилгээний анги."""
    
    def __init__(self, date: Optional[str] = None):
        """
        Цуглуулагч үйлчилгээг эхлүүлэх.
        
        Args:
            date: Огноо ISO форматаар (YYYY-MM-DD). Өнөөдөр байна.
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
        """Бүх цуглуулагчдыг ажиллуулж үр дүнг өгөгдлийн санд хадгалах."""
        db = SessionLocal()
        try:
            for crawler in self.crawlers:
                try:
                    rates = crawler.crawl()
                    if rates:
                        bank_name = crawler.__class__.__name__.replace("Crawler", "")
                        exchange_rate_data = ExchangeRate(
                            date=self.date,
                            bank=bank_name,
                            rates=rates
                        )
                        repository.save_rates(db, exchange_rate_data)
                        logger.info(f"Successfully crawled and saved rates from {bank_name}")
                except Exception as e:
                    logger.error(f"Failed to crawl from {crawler.__class__.__name__}: {e}")
        finally:
            db.close()
    
    def scrape_bank(self, bank_name: str) -> Optional[Dict[str, CurrencyDetail]]:
        """
        Тодорхой банкнаас ханшийг татах, өгөгдлийн санд хадгалахгүй.
        
        Args:
            bank_name: Татах банкны нэр (том жижиг үсэг ялгахгүй)
            
        Returns:
            Валютын ханшийн толь эсвэл банк олдоогүй бол None
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



