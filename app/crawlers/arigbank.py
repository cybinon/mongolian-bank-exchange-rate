from typing import Dict

from app.config import config
from app.crawlers.base import BaseCrawler
from app.models.exchange_rate import CurrencyDetail
from app.utils.logger import logger


class ArigBank(BaseCrawler):
    BANK_NAME = "ArigBank"

    def crawl(self) -> Dict[str, CurrencyDetail]:
        token = (config.ARIGBANK_BEARER_TOKEN or "").strip()
        if not token:
            logger.warning("ArigBank: ARIGBANK_BEARER_TOKEN not configured")
            return {}

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        resp = self.post(
            config.ARIGBANK_API_URL,
            headers=headers,
            json={"rateDate": self.date.replace("-", "")},
        )
        resp.raise_for_status()

        data = resp.json()
        if not data.get("data") and data.get("message"):
            logger.warning(f"ArigBank API error: {data.get('message')}")
            return {}

        return self._parse(data.get("data", []))

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
