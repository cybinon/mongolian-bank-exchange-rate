"""Scheduled job runner for bank exchange rate crawling.

Runs hourly to ensure crawls happen even with Heroku dyno restarts.
"""

import time

import schedule

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


def main():
    ensure_playwright_browsers()
    init_db()

    # Run hourly to handle Heroku dyno restarts (every 24h)
    schedule.every().hour.do(job)
    logger.info("Scheduled hourly crawl job")

    logger.info("Running initial crawl")
    job()

    logger.info("Starting scheduler")
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()
