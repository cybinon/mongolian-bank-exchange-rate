import os
from typing import Dict, Optional

import requests
import urllib3
from dotenv import load_dotenv

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from app.models.exchange_rate import CurrencyDetail, Rate


class KhanBankCrawler:
    BANK_NAME = "KhanBank"
    REQUEST_TIMEOUT = 30

    def __init__(self, url: str, date: str):
        self.url = url
        self.date = date
        self.ssl_verify = os.getenv("SSL_VERIFY", "True").lower() in ("true", "1", "t")

    def crawl(self) -> Dict[str, CurrencyDetail]:
        endpoint = f"{self.url}?date={self.date}"
        response = requests.get(url=endpoint, verify=self.ssl_verify, timeout=self.REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()

        if not isinstance(data, list):
            raise ValueError(f"Expected list response, got {type(data)}")

        return self._parse_rates(data)

    def _parse_rates(self, data: list) -> Dict[str, CurrencyDetail]:
        rates = {}

        for item in data:
            currency_code = item.get("currency")
            if not currency_code:
                continue

            try:
                rates[currency_code.lower()] = CurrencyDetail(
                    cash=Rate(
                        buy=self._parse_rate_value(item.get("cashBuyRate")),
                        sell=self._parse_rate_value(item.get("cashSellRate")),
                    ),
                    noncash=Rate(
                        buy=self._parse_rate_value(item.get("buyRate")),
                        sell=self._parse_rate_value(item.get("sellRate")),
                    ),
                )
            except Exception:
                continue

        return rates

    @staticmethod
    def _parse_rate_value(value) -> Optional[float]:
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
