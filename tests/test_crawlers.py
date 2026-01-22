import datetime
from unittest.mock import MagicMock, patch

import pytest

from app.crawlers.base_crawler import BaseCrawler
from app.crawlers.capitronbank import CapitronBankCrawler
from app.crawlers.golomt import GolomtBankCrawler
from app.crawlers.khanbank import KhanBankCrawler


class TestKhanBankCrawler:
    @patch("app.crawlers.khanbank.requests.get")
    def test_crawl_success(self, mock_get, sample_khanbank_response):
        mock_response = MagicMock()
        mock_response.json.return_value = sample_khanbank_response
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        crawler = KhanBankCrawler("https://test.url", datetime.date.today().isoformat())
        rates = crawler.crawl()

        assert rates is not None
        assert "usd" in rates
        assert rates["usd"].cash.buy == 3420.5
        assert rates["usd"].cash.sell == 3450.0
        assert rates["usd"].noncash.buy == 3415.0
        assert rates["usd"].noncash.sell == 3455.0

    @patch("app.crawlers.khanbank.requests.get")
    def test_crawl_empty_response(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        crawler = KhanBankCrawler("https://test.url", datetime.date.today().isoformat())
        rates = crawler.crawl()

        assert rates == {}

    @patch("app.crawlers.khanbank.requests.get")
    def test_crawl_network_error(self, mock_get):
        mock_get.side_effect = Exception("Network error")

        crawler = KhanBankCrawler("https://test.url", datetime.date.today().isoformat())

        with pytest.raises(Exception):
            crawler.crawl()


class TestGolomtBankCrawler:
    @patch("app.crawlers.golomt.requests.get")
    def test_crawl_success(self, mock_get, sample_golomt_response):
        mock_response = MagicMock()
        mock_response.json.return_value = sample_golomt_response
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        crawler = GolomtBankCrawler("https://test.url", datetime.date.today().isoformat())
        rates = crawler.crawl()

        assert rates is not None
        assert "usd" in rates
        assert rates["usd"].cash.buy == 3420.5

    @patch("app.crawlers.golomt.requests.get")
    def test_crawl_empty_data(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": {}}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        crawler = GolomtBankCrawler("https://test.url", datetime.date.today().isoformat())
        rates = crawler.crawl()

        assert rates == {}


class TestCapitronBankCrawler:
    @patch("app.crawlers.capitronbank.requests.get")
    def test_crawl_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "currency_code": "USD",
                "buy_rate": 3420.0,
                "sell_rate": 3450.0,
                "buy_rate_noncash": 3415.0,
                "sell_rate_noncash": 3455.0,
            }
        ]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        crawler = CapitronBankCrawler("https://test.url", datetime.date.today().isoformat())
        rates = crawler.crawl()

        assert rates is not None


class TestBaseCrawlerParseFloat:
    """Test the _parse_float method from BaseCrawler via a concrete implementation."""

    def test_parse_float_valid_number(self):
        class TestCrawler(BaseCrawler):
            def crawl(self):
                pass

            def _parse_rates(self, data):
                pass

        crawler = TestCrawler("https://test.url", datetime.date.today().isoformat())
        assert crawler._parse_float(3420.5) == 3420.5
        assert crawler._parse_float("3420.5") == 3420.5
        assert crawler._parse_float("3,420.5") == 3420.5

    def test_parse_float_invalid_input(self):
        class TestCrawler(BaseCrawler):
            def crawl(self):
                pass

            def _parse_rates(self, data):
                pass

        crawler = TestCrawler("https://test.url", datetime.date.today().isoformat())
        assert crawler._parse_float(None) is None
        assert crawler._parse_float("") is None
        assert crawler._parse_float("-") is None
        assert crawler._parse_float(0) is None

    def test_parse_float_with_whitespace(self):
        class TestCrawler(BaseCrawler):
            def crawl(self):
                pass

            def _parse_rates(self, data):
                pass

        crawler = TestCrawler("https://test.url", datetime.date.today().isoformat())
        assert crawler._parse_float(" 3420.5 ") == 3420.5
        assert crawler._parse_float("3 420.5") == 3420.5
