"""
Scheduler program to collect exchange rates from all banks on a schedule.
The schedule is controlled by the CRON_SCHEDULE environment variable.
"""
import schedule
import time
from app.services.scraper_service import ScraperService
from app.db.database import init_db
from app.utils.logger import get_logger
from app.config import config
from datetime import datetime

logger = get_logger(__name__)


def job():
    """Run the scraping job once."""
    logger.info("=" * 60)
    logger.info(f"Starting scheduled crawl job at {datetime.now()}")
    logger.info("=" * 60)
    
    try:
        scraper = ScraperService()
        scraper.run_crawlers()
        logger.info("Scheduled crawl job completed successfully")
    except Exception as e:
        logger.error(f"Scheduled crawl job failed: {e}", exc_info=True)
    
    logger.info("=" * 60)


def parse_cron_schedule(cron_string: str) -> dict:
    """
    Parse a cron schedule string into simple schedule parameters.

    Format: minute hour day month day_of_week
    Example: "0 1 * * *" means every day at 01:00.

    Args:
        cron_string: Cron expression string

    Returns:
        Dict with schedule parameters
    """
    parts = cron_string.split()
    if len(parts) != 5:
        logger.warning(f"Invalid cron format: {cron_string}. Using default: daily at 01:00")
        return {"time": "01:00"}
    
    minute, hour, day, month, day_of_week = parts
    
    # Simple cron parser — handles common daily schedule
    if day == "*" and month == "*" and day_of_week == "*":
        # Daily schedule
        time_str = f"{hour.zfill(2)}:{minute.zfill(2)}"
        return {"type": "daily", "time": time_str}
    else:
        logger.warning(f"Complex cron schedule not fully supported: {cron_string}")
        logger.warning("Using default: daily at 01:00")
        return {"type": "daily", "time": "01:00"}


def main():
    """Entry point to start the scheduler."""
    logger.info("=" * 60)
    logger.info("Starting Mongolian Bank Exchange Rate Crawler Scheduler")
    logger.info("=" * 60)
    logger.info(f"Cron Schedule: {config.CRON_SCHEDULE}")
    logger.info("Initializing database (creating tables if missing)...")
    try:
        init_db()
        logger.info("Database initialized.")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}", exc_info=True)
    
    # Parse and apply schedule
    schedule_params = parse_cron_schedule(config.CRON_SCHEDULE)
    
    if schedule_params["type"] == "daily":
        schedule.every().day.at(schedule_params["time"]).do(job)
    logger.info(f"Scheduled to run daily at {schedule_params['time']}")
    
    logger.info("Scheduler started. Press Ctrl+C to stop.")
    logger.info("=" * 60)
    
    # Run once on startup (optional)
    logger.info("Running initial crawl on startup...")
    job()
    
    # Keep the scheduler running
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
    except Exception as e:
        logger.error(f"Scheduler error: {e}", exc_info=True)


if __name__ == "__main__":
    main()
