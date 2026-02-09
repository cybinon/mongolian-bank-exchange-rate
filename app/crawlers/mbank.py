"""MBank crawler using Playwright to intercept API response."""

from typing import Dict

from app.config import config
from app.crawlers.base import PlaywrightCrawler
from app.models.exchange_rate import CurrencyDetail


class MBank(PlaywrightCrawler):
    BANK_NAME = "MBank"

    def _crawl_page(self, page) -> Dict[str, CurrencyDetail]:
        api_data = {}

        def handle_response(response):
            if "api?name=getCurrencyList" in response.url:
                try:
                    api_data["result"] = response.json()
                except Exception:
                    pass

        page.on("response", handle_response)
        page.goto(
            config.MBANK_URI,
            timeout=self.timeout,
            wait_until="networkidle",
        )

        button = page.locator("xpath=/html/body/div/div/div[2]/button")
        if button.count() > 0:
            button.click()
            page.wait_for_timeout(3000)
        else:
            alt = page.locator("text=Валютын ханш").first
            if alt.count() > 0:
                alt.click()
                page.wait_for_timeout(3000)

        if "result" in api_data:
            return self._parse(api_data["result"])
        return {}

    def _parse(self, data: dict) -> Dict[str, CurrencyDetail]:
        rates = {}
        if not data.get("success"):
            return rates
        for item in data.get("data", []):
            code = (item.get("fxd_crncy_code") or "").lower()
            if code:
                buy = self.parse_float(item.get("buy_rate"))
                sell = self.parse_float(item.get("sale_rate"))
                rates[code] = self.make_rate(buy, sell, buy, sell)
        return rates
