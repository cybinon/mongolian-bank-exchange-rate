import os
from typing import Dict

import requests
import urllib3
from dotenv import load_dotenv

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from app.models.exchange_rate import CurrencyDetail, Rate


class StateBankCrawler:
    BANK_NAME = "StateBank"
    REQUEST_TIMEOUT = 30

    def __init__(self, url: str, date: str):
        self.url = url
        self.date = date
        self.ssl_verify = os.getenv("SSL_VERIFY", "True").lower() in ("true", "1", "t")

    def crawl(self) -> Dict[str, CurrencyDetail]:
        response = requests.get(url=self.url, verify=self.ssl_verify, timeout=self.REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()

        if not isinstance(data, list):
            raise ValueError(f"Expected list, got {type(data)}")

        return self._parse_rates(data)

    def _parse_rates(self, data: list) -> Dict[str, CurrencyDetail]:
        rates = {}

        for item in data:
            currency_code = item.get("curCode", "").lower()

            if not currency_code or currency_code == "mnt":
                continue

            cash_buy = item.get("cashBuy", 0)
            cash_sell = item.get("cashSale", 0)
            noncash_buy = item.get("nonCashBuy", 0)
            noncash_sell = item.get("nonCashSale", 0)

            if cash_buy or cash_sell or noncash_buy or noncash_sell:
                rates[currency_code] = CurrencyDetail(
                    cash=Rate(buy=float(cash_buy) if cash_buy else 0.0, sell=float(cash_sell) if cash_sell else 0.0),
                    noncash=Rate(
                        buy=float(noncash_buy) if noncash_buy else 0.0,
                        sell=float(noncash_sell) if noncash_sell else 0.0,
                    ),
                )

        return rates
