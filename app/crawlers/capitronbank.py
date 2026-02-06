from typing import Dict

from app.config import config
from app.crawlers.base import BaseCrawler
from app.models.exchange_rate import CurrencyDetail


class CapitronBank(BaseCrawler):
    BANK_NAME = "CapitronBank"

    def crawl(self) -> Dict[str, CurrencyDetail]:
        resp = self.get(config.CAPITRONBANK_API_URL)
        resp.raise_for_status()
        return self._parse(resp.json())

    def _parse(self, data: list) -> Dict[str, CurrencyDetail]:
        rates = {}
        for item in data:
            code = item.get("currencyCode", "").lower()
            if code:
                rates[code] = self.make_rate(
                    cash_buy=self.parse_float(item.get("cashBuyRate")),
                    cash_sell=self.parse_float(item.get("cashSellRate")),
                    noncash_buy=self.parse_float(item.get("transferBuyRate")),
                    noncash_sell=self.parse_float(
                        item.get("transferSellRate")
                    ),
                )
        return rates
