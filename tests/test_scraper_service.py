import datetime
from unittest.mock import MagicMock, patch

from app.services.scraper_service import ScraperService


class TestScraperService:
    def test_init_with_default_date(self):
        service = ScraperService()
        assert service.date == datetime.date.today().isoformat()

    def test_init_with_custom_date(self):
        service = ScraperService(date="2026-01-15")
        assert service.date == "2026-01-15"

    def test_crawlers_count(self):
        service = ScraperService()
        assert len(service.crawlers) == 13

    @patch.object(ScraperService, "_execute_crawler")
    @patch.object(ScraperService, "_save_results")
    def test_run_crawlers_sequential(self, mock_save, mock_execute):
        mock_execute.return_value = ("TestBank", {"usd": {}}, None)

        with patch("app.services.scraper_service.config") as mock_config:
            mock_config.ENABLE_PARALLEL = False
            service = ScraperService()
            service.run_crawlers()

        assert mock_execute.call_count == 13
        mock_save.assert_called_once()

    def test_group_crawlers(self):
        service = ScraperService()
        groups = service._group_crawlers()

        assert "playwright" in groups
        assert "http" in groups
        assert len(groups["playwright"]) == 6
        assert len(groups["http"]) == 7

    def test_execute_crawler_success(self):
        service = ScraperService()
        mock_crawler = MagicMock()
        mock_crawler.__class__.__name__ = "TestBankCrawler"
        mock_crawler.crawl.return_value = {"usd": {}}

        bank_name, rates, error = service._execute_crawler(mock_crawler)

        assert bank_name == "TestBank"
        assert rates == {"usd": {}}
        assert error is None

    def test_execute_crawler_failure(self):
        service = ScraperService()
        mock_crawler = MagicMock()
        mock_crawler.__class__.__name__ = "TestBankCrawler"
        mock_crawler.crawl.side_effect = Exception("Test error")

        bank_name, rates, error = service._execute_crawler(mock_crawler)

        assert bank_name == "TestBank"
        assert rates is None
        assert error is not None


class TestScrapeBankMethod:
    def test_scrape_known_bank(self):
        with patch("app.crawlers.khanbank.KhanBankCrawler.crawl") as mock_crawl:
            mock_crawl.return_value = {"usd": {}}

            service = ScraperService()
            result = service.scrape_bank("khanbank")

            assert result is not None

    def test_scrape_unknown_bank(self):
        service = ScraperService()
        result = service.scrape_bank("unknown_bank")

        assert result is None

    def test_scrape_bank_case_insensitive(self):
        with patch("app.crawlers.khanbank.KhanBankCrawler.crawl") as mock_crawl:
            mock_crawl.return_value = {"usd": {}}

            service = ScraperService()

            result1 = service.scrape_bank("KhanBank")
            result2 = service.scrape_bank("KHANBANK")
            result3 = service.scrape_bank("khanbank")

            assert result1 is not None
            assert result2 is not None
            assert result3 is not None
