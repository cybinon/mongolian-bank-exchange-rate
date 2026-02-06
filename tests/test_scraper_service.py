import datetime
from unittest.mock import MagicMock, patch

from app.services.scraper import ScraperService


class TestScraperService:
    def test_init_default_date(self):
        service = ScraperService()
        assert service.date == datetime.date.today().isoformat()

    def test_init_custom_date(self):
        service = ScraperService(date="2026-01-15")
        assert service.date == "2026-01-15"

    def test_execute_success(self):
        service = ScraperService()
        mock_crawler_cls = MagicMock()
        mock_crawler_cls.BANK_NAME = "TestBank"
        mock_crawler = MagicMock()
        mock_crawler.crawl.return_value = {"usd": {}}
        mock_crawler_cls.return_value = mock_crawler

        bank, rates, error = service._execute(mock_crawler_cls)

        assert bank == "TestBank"
        assert rates == {"usd": {}}
        assert error is None

    def test_execute_failure(self):
        service = ScraperService()
        mock_crawler_cls = MagicMock()
        mock_crawler_cls.BANK_NAME = "TestBank"
        mock_crawler = MagicMock()
        mock_crawler.crawl.side_effect = Exception("Error")
        mock_crawler_cls.return_value = mock_crawler

        bank, rates, error = service._execute(mock_crawler_cls)

        assert bank == "TestBank"
        assert rates is None
        assert error is not None


class TestScrapeBankMethod:
    @patch("app.crawlers.khanbank.KhanBank.crawl")
    def test_scrape_known_bank(self, mock_crawl):
        mock_crawl.return_value = {"usd": {}}
        service = ScraperService()
        result = service.scrape_bank("khanbank")
        assert result is not None

    def test_scrape_unknown_bank(self):
        service = ScraperService()
        result = service.scrape_bank("unknown_bank")
        assert result is None
