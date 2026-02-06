from app.services.scraper import ScraperService
from app.utils.playwright_setup import ensure_playwright_browsers


def main():
    ensure_playwright_browsers()
    ScraperService().run_all()


if __name__ == "__main__":
    main()
