import os
from typing import Dict, Optional

import requests
import urllib3
from dotenv import load_dotenv

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from app.models.exchange_rate import CurrencyDetail, Rate


class GolomtBankCrawler:
    BANK_NAME = "GolomtBank"
    REQUEST_TIMEOUT = 30

    def __init__(self, url: str, date: str):
        self.url = url
        self.date = date
        self.ssl_verify = os.getenv("SSL_VERIFY", "True").lower() in ("true", "1", "t")

    def crawl(self) -> Dict[str, CurrencyDetail]:
        date_formatted = self.date.replace("-", "")
        endpoint = f"{self.url}?date={date_formatted}"

        response = requests.get(url=endpoint, verify=self.ssl_verify, timeout=self.REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()

        if not isinstance(data, dict) or "result" not in data:
            raise ValueError(f"Expected dict with 'result' key, got {type(data)}")

        return self._parse_rates(data["result"])

    def _parse_rates(self, data: dict) -> Dict[str, CurrencyDetail]:
        rates = {}

        for currency_code, currency_data in data.items():
            if not isinstance(currency_data, dict):
                continue

            try:
                cash_buy = currency_data.get("cash_buy", {})
                cash_sell = currency_data.get("cash_sell", {})
                non_cash_buy = currency_data.get("non_cash_buy", {})
                non_cash_sell = currency_data.get("non_cash_sell", {})

                rates[currency_code.lower()] = CurrencyDetail(
                    cash=Rate(
                        buy=self._parse_rate_value(cash_buy.get("cvalue")),
                        sell=self._parse_rate_value(cash_sell.get("cvalue")),
                    ),
                    noncash=Rate(
                        buy=self._parse_rate_value(non_cash_buy.get("cvalue")),
                        sell=self._parse_rate_value(non_cash_sell.get("cvalue")),
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
