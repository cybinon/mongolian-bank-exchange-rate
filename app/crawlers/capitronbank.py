import os
from typing import Dict, Optional

import requests
import urllib3
from dotenv import load_dotenv

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from app.models.exchange_rate import CurrencyDetail, Rate


class CapitronBankCrawler:
    BANK_NAME = "CapitronBank"
    REQUEST_TIMEOUT = 30
    API_URL = "https://www.capitronbank.mn/admin/en/wp-json/bank/rates/capitronbank"

    def __init__(self, url: str, date: str):
        self.url = url
        self.date = date
        self.ssl_verify = os.getenv("SSL_VERIFY", "True").lower() in ("true", "1", "t")

    def crawl(self) -> Dict[str, CurrencyDetail]:
        response = requests.get(url=self.API_URL, verify=self.ssl_verify, timeout=self.REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()

        if not isinstance(data, list):
            raise ValueError(f"Expected list, got {type(data)}")

        return self._parse_rates(data)

    def _parse_rates(self, data: list) -> Dict[str, CurrencyDetail]:
        rates = {}

        for item in data:
            currency_code = item.get("curcode", "").lower()
            rtypecode = item.get("rtypecode", "")

            if not currency_code or currency_code == "mnt":
                continue

            if currency_code not in rates:
                rates[currency_code] = CurrencyDetail(cash=Rate(buy=0.0, sell=0.0), noncash=Rate(buy=0.0, sell=0.0))

            buy_rate = self._parse_float(item.get("buyrate", "0"))
            sell_rate = self._parse_float(item.get("salerate", "0"))

            if rtypecode == "1":
                rates[currency_code].cash.buy = buy_rate if buy_rate else 0.0
                rates[currency_code].cash.sell = sell_rate if sell_rate else 0.0
            elif rtypecode == "2":
                rates[currency_code].noncash.buy = buy_rate if buy_rate else 0.0
                rates[currency_code].noncash.sell = sell_rate if sell_rate else 0.0

        return rates

    def _parse_float(self, value) -> Optional[float]:
        if not value:
            return None
        try:
            if isinstance(value, str):
                cleaned = value.replace(",", "").strip()
                return float(cleaned)
            return float(value)
        except (ValueError, AttributeError):
            return None
