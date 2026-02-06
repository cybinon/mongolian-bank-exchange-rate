"""Scheduled job runner for bank exchange rate crawling."""

import time

import schedule

from app.config import config
from app.db.database import init_db
from app.services.scraper import ScraperService
from app.utils.logger import logger
from app.utils.playwright_setup import ensure_playwright_browsers


def job():
    logger.info("Starting scheduled crawl")
    try:
        ScraperService().run_all()
        logger.info("Crawl completed")
    except Exception as e:
        logger.error(f"Crawl failed: {e}")


def parse_cron(cron: str) -> str:
    parts = cron.split()
    if len(parts) == 5:
        return f"{parts[1].zfill(2)}:{parts[0].zfill(2)}"
    return "01:00"


def main():
    ensure_playwright_browsers()
    init_db()

    time_str = parse_cron(config.CRON_SCHEDULE)
    schedule.every().day.at(time_str).do(job)
    logger.info(f"Scheduled daily job at {time_str}")

    logger.info("Running initial crawl")
    job()

    logger.info("Starting scheduler")
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()
