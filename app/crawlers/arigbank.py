from typing import Dict

from app.config import config
from app.crawlers.base import BaseCrawler
from app.models.exchange_rate import CurrencyDetail


class ArigBank(BaseCrawler):
    BANK_NAME = "ArigBank"

    def crawl(self) -> Dict[str, CurrencyDetail]:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config.ARIGBANK_BEARER_TOKEN}",
        }
        resp = self.post(
            config.ARIGBANK_API_URL,
            headers=headers,
            json={"rateDate": self.date.replace("-", "")},
        )
        resp.raise_for_status()
        return self._parse(resp.json().get("data", []))

    def _parse(self, data: list) -> Dict[str, CurrencyDetail]:
        rates = {}
        for item in data:
            code = item.get("curCode", "").strip().lower()
            if code:
                rates[code] = self.make_rate(
                    cash_buy=self.parse_float(item.get("belenBuyRate")),
                    cash_sell=self.parse_float(item.get("belenSellRate")),
                    noncash_buy=self.parse_float(item.get("belenBusBuyRate")),
                    noncash_sell=self.parse_float(
                        item.get("belenBusSellRate")
                    ),
                )
        return rates
