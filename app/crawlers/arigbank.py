from typing import Dict

import requests
import urllib3
from dotenv import load_dotenv

from app.config import config
from app.models.exchange_rate import CurrencyDetail, Rate

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ArigBankCrawler:
    BANK_NAME = "ArigBank"

    def __init__(self, url: str, date: str):
        self.url = url
        self.date = date
        self.API_URL = config.ARIGBANK_API_URL
        self.bearer_token = config.ARIGBANK_BEARER_TOKEN
        self.ssl_verify = config.SSL_VERIFY
        self.timeout = config.REQUEST_TIMEOUT

    def crawl(self) -> Dict[str, CurrencyDetail]:
        date_str = self.date.replace("-", "")
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.bearer_token}"}
        payload = {"rateDate": date_str}

        response = requests.post(
            url=self.API_URL, headers=headers, json=payload, verify=self.ssl_verify, timeout=self.timeout
        )
        response.raise_for_status()
        result = response.json()
        data = result.get("data", [])

        if not isinstance(data, list):
            raise ValueError(f"Expected list in data field, got {type(data)}")

        return self._parse_rates(data)

    def _parse_rates(self, data: list) -> Dict[str, CurrencyDetail]:
        rates = {}
        for item in data:
            try:
                currency_code = item["curCode"].strip().lower()
                rates[currency_code] = CurrencyDetail(
                    cash=Rate(
                        buy=float(item["belenBuyRate"]) if item["belenBuyRate"] else None,
                        sell=float(item["belenSellRate"]) if item["belenSellRate"] else None,
                    ),
                    noncash=Rate(
                        buy=float(item["belenBusBuyRate"]) if item["belenBusBuyRate"] else None,
                        sell=float(item["belenBusSellRate"]) if item["belenBusSellRate"] else None,
                    ),
                )
            except (KeyError, ValueError):
                continue

        return rates
