import time

import schedule

from app.config import config
from app.db.database import init_db
from app.services.scraper_service import ScraperService
from app.utils.logger import get_logger
from app.utils.playwright_setup import ensure_playwright_browsers

logger = get_logger("cron")


def job():
    logger.info("Starting scheduled crawl job")
    try:
        scraper = ScraperService()
        scraper.run_crawlers()
        logger.info("Crawl job completed successfully")
    except Exception as e:
        logger.exception(f"Crawl job failed: {e}")


def parse_cron_schedule(cron_string: str) -> dict:
    parts = cron_string.split()
    if len(parts) != 5:
        return {"type": "daily", "time": "01:00"}

    minute, hour, day, month, day_of_week = parts

    if day == "*" and month == "*" and day_of_week == "*":
        time_str = f"{hour.zfill(2)}:{minute.zfill(2)}"
        return {"type": "daily", "time": time_str}
    return {"type": "daily", "time": "01:00"}


def main():
    ensure_playwright_browsers()
    init_db()
    logger.info("Database initialized")

    schedule_params = parse_cron_schedule(config.CRON_SCHEDULE)

    if schedule_params["type"] == "daily":
        schedule.every().day.at(schedule_params["time"]).do(job)
        logger.info(f"Scheduled daily job at {schedule_params['time']}")

    logger.info("Running initial crawl job")
    job()

    logger.info("Starting scheduler loop")
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()
