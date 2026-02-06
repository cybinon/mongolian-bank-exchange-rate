"""MBank crawler using Playwright for JavaScript rendering."""

from typing import Dict

from app.config import config
from app.crawlers.base import PlaywrightCrawler
from app.models.exchange_rate import CurrencyDetail


class MBank(PlaywrightCrawler):
    BANK_NAME = "MBank"

    def _crawl_page(self, page) -> Dict[str, CurrencyDetail]:
        page.goto(
            config.MBANK_URI,
            timeout=self.timeout,
            wait_until="networkidle",
        )
        page.wait_for_timeout(3000)

        button = page.locator("xpath=/html/body/div/div/div[2]/button")
        if button.count() > 0:
            button.click()
            page.wait_for_timeout(5000)
        else:
            alt = page.locator("text=Валютын ханш").first
            if alt.count() > 0:
                alt.click()
                page.wait_for_timeout(5000)

        rates = {}
        xpath = "xpath=/html/body/div/div/div[2]/div[4]/div[2]"
        container = page.locator(xpath)
        if container.count() == 0:
            container = page.locator("div.relative.overflow-x-auto")
        if container.count() == 0:
            return rates

        selector = r"div.flex.min-w-\[760px\].bg-white"
        for row in container.locator(selector).all():
            currency_el = row.locator("p.font-semibold").first
            if currency_el.count() == 0:
                continue
            code = (currency_el.text_content() or "").strip().lower()
            if not code or len(code) != 3 or code in rates:
                continue

            els = row.locator("p.font-regular").all()
            if len(els) >= 4:
                buy = self.parse_float(els[2].text_content())
                sell = self.parse_float(els[3].text_content())
                if buy and sell:
                    rates[code] = self.make_rate(buy, sell, buy, sell)
        return rates
