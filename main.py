from app.services.scraper_service import ScraperService
from app.utils.playwright_setup import ensure_playwright_browsers


def main():
    ensure_playwright_browsers()
    scraper = ScraperService()
    scraper.run_crawlers()


if __name__ == "__main__":
    main()
