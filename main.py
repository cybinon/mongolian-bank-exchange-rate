from app.services.scraper_service import ScraperService

def main():
    scraper = ScraperService()
    scraper.run_crawlers()

if __name__ == "__main__":
    main()
