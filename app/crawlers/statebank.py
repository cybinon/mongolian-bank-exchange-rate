from typing import Dict

from app.config import config
from app.crawlers.base import BaseCrawler
from app.models.exchange_rate import CurrencyDetail


class StateBank(BaseCrawler):
    BANK_NAME = "StateBank"

    def crawl(self) -> Dict[str, CurrencyDetail]:
        resp = self.get(config.STATEBANK_URI)
        resp.raise_for_status()
        return self._parse(resp.json().get("data", []))

    def _parse(self, data: list) -> Dict[str, CurrencyDetail]:
        rates = {}
        for item in data:
            code = item.get("CurrencyCode", "").lower()
            if code:
                rates[code] = self.make_rate(
                    cash_buy=self.parse_float(item.get("BuyRate")),
                    cash_sell=self.parse_float(item.get("SellRate")),
                )
        return rates
