from abc import ABC, abstractmethod
from typing import Dict, Optional

import urllib3
from dotenv import load_dotenv

from app.config import config
from app.models.exchange_rate import CurrencyDetail
from app.utils.logger import get_logger

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = get_logger(__name__)


class BaseCrawler(ABC):
    BANK_NAME: str = "BaseBank"

    def __init__(self, url: str, date: str):
        self.url = url
        self.date = date
        self.ssl_verify = config.SSL_VERIFY
        self.timeout = config.REQUEST_TIMEOUT

    @abstractmethod
    def crawl(self) -> Dict[str, CurrencyDetail]:
        pass

    @abstractmethod
    def _parse_rates(self, data) -> Dict[str, CurrencyDetail]:
        pass

    def _parse_float(self, value) -> Optional[float]:
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
        pass

    def _log_error(self, error: Exception, context: str = ""):
        error_msg = f"Error in {self.BANK_NAME}"
        if context:
            error_msg += f" ({context})"
        error_msg += f": {error}"
        logger.error(error_msg)
