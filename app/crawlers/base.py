from abc import ABC, abstractmethod
from typing import Dict, Optional

import requests
from playwright.sync_api import sync_playwright

from app.config import config
from app.models.exchange_rate import CurrencyDetail, Rate


class BaseCrawler(ABC):
    """Base class for HTTP API crawlers."""

    BANK_NAME: str = ""

    def __init__(self, date: str):
        self.date = date
        self.timeout = config.REQUEST_TIMEOUT
        self.ssl_verify = config.SSL_VERIFY

    @abstractmethod
    def crawl(self) -> Dict[str, CurrencyDetail]:
        pass

    def get(self, url: str, **kwargs) -> requests.Response:
        return requests.get(
            url, verify=self.ssl_verify, timeout=self.timeout, **kwargs
        )

    def post(self, url: str, **kwargs) -> requests.Response:
        return requests.post(
            url, verify=self.ssl_verify, timeout=self.timeout, **kwargs
        )

    @staticmethod
    def parse_float(value) -> Optional[float]:
        if value is None:
            return None
        try:
            if isinstance(value, (int, float)):
                return float(value) if value != 0 else None
            cleaned = (
                str(value)
                .strip()
                .replace(",", "")
                .replace(" ", "")
                .replace("\xa0", "")
            )
            if not cleaned or cleaned == "-" or cleaned == "0":
                return None
            return float(cleaned)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def make_rate(
        cash_buy=None, cash_sell=None, noncash_buy=None, noncash_sell=None
    ) -> CurrencyDetail:
        return CurrencyDetail(
            cash=Rate(buy=cash_buy, sell=cash_sell),
            noncash=Rate(buy=noncash_buy, sell=noncash_sell),
        )


class PlaywrightCrawler(BaseCrawler):
    """Base class for Playwright-based crawlers."""

    def __init__(self, date: str):
        super().__init__(date)
        self.timeout = config.PLAYWRIGHT_TIMEOUT

    def crawl(self) -> Dict[str, CurrencyDetail]:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                ignore_https_errors=not self.ssl_verify
            )
            context.set_default_timeout(self.timeout)
            page = context.new_page()
            try:
                rates = self._crawl_page(page)
            finally:
                browser.close()
        return rates

    @abstractmethod
    def _crawl_page(self, page) -> Dict[str, CurrencyDetail]:
        pass
