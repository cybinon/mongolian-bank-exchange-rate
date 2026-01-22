import os
from typing import Dict, Optional

import requests
import urllib3
from dotenv import load_dotenv

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from app.models.exchange_rate import CurrencyDetail, Rate


class MongolBankCrawler:
    BANK_NAME = "MongolBank"
    REQUEST_TIMEOUT = 30
    API_URL = "https://www.mongolbank.mn/en/currency-rate-movement/data"

    def __init__(self, url: str, date: str):
        self.url = url
        self.date = date
        self.ssl_verify = os.getenv("SSL_VERIFY", "True").lower() in ("true", "1", "t")

    def crawl(self) -> Dict[str, CurrencyDetail]:
        response = requests.post(url=self.API_URL, verify=self.ssl_verify, timeout=self.REQUEST_TIMEOUT)
        response.raise_for_status()
        json_data = response.json()

        if not json_data.get("success"):
            raise ValueError("API returned success=false")

        data = json_data.get("data", [])
        if not isinstance(data, list) or len(data) == 0:
            raise ValueError("Expected non-empty list in data field")

        return self._parse_rates(data[0])

    def _parse_rates(self, data: dict) -> Dict[str, CurrencyDetail]:
        rates = {}

        for key, value in data.items():
            if key == "RATE_DATE":
                continue

            if value and value != "-":
                currency_code = key.lower()
                rate_value = self._parse_rate_value(value)

                if rate_value is not None:
                    rates[currency_code] = CurrencyDetail(
                        cash=Rate(buy=rate_value, sell=rate_value), noncash=Rate(buy=rate_value, sell=rate_value)
                    )

        return rates

    def _parse_rate_value(self, value: Optional[str]) -> Optional[float]:
        if not value:
            return None
        try:
            cleaned = value.replace(",", "").strip()
            return float(cleaned)
        except (ValueError, AttributeError):
            return None
