"""CKBank crawler using Playwright for JavaScript rendering."""

import re
from typing import Dict

from app.config import config
from app.crawlers.base import PlaywrightCrawler
from app.models.exchange_rate import CurrencyDetail


class CKBank(PlaywrightCrawler):
    BANK_NAME = "CKBank"

    def _crawl_page(self, page) -> Dict[str, CurrencyDetail]:
        page.goto(
            config.CKBANK_URI,
            timeout=self.timeout,
            wait_until="networkidle",
        )

        rates = {}
        selector = "table tbody tr, .uk-table tbody tr"
        for row in page.locator(selector).all():
            cells = row.locator("td").all()
            if len(cells) >= 6:
                text = cells[0].text_content() or ""
                match = re.search(r"\b([A-Z]{3})\b", text)
                if match:
                    code = match.group(1).lower()
                    if code not in rates:
                        c2 = cells[2].text_content()
                        c3 = cells[3].text_content()
                        c4 = cells[4].text_content()
                        c5 = cells[5].text_content()
                        rates[code] = self.make_rate(
                            cash_buy=self.parse_float(c2),
                            cash_sell=self.parse_float(c3),
                            noncash_buy=self.parse_float(c4),
                            noncash_sell=self.parse_float(c5),
                        )
        return rates
