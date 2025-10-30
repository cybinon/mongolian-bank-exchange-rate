"""
Бүх банкнаас валютын ханшийг тогтмол цуглуулах хуваарийн програм.
Хуваарь нь CRON_SCHEDULE орчны хувьсагчаар тохируулагддаг.
"""
import schedule
import time
from app.services.scraper_service import ScraperService
from app.utils.logger import get_logger
from app.config import config
from datetime import datetime

logger = get_logger(__name__)


def job():
    """Цуглуулах ажлыг гүйцэтгэх."""
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
    Cron хуваарийн мөрийг хуваарийн параметрүүд рүү задлах.
    
    Формат: минут цаг өдөр сар долоо хоногийн өдөр
    Жишээ: "0 1 * * *" гэдэг нь өдөр бүр 1:00 цагт гэсэн үг
    
    Args:
        cron_string: Cron хуваарийн мөр
        
    Returns:
        Хуваарийн параметрүүдтэй толь
    """
    parts = cron_string.split()
    if len(parts) != 5:
        logger.warning(f"Invalid cron format: {cron_string}. Using default: daily at 01:00")
        return {"time": "01:00"}
    
    minute, hour, day, month, day_of_week = parts
    
    # Энгийн cron задлагч - үндсэн тохиолдлуудыг зохицуулна
    if day == "*" and month == "*" and day_of_week == "*":
        # Өдөр бүрийн хуваарь
        time_str = f"{hour.zfill(2)}:{minute.zfill(2)}"
        return {"type": "daily", "time": time_str}
    else:
        logger.warning(f"Complex cron schedule not fully supported: {cron_string}")
        logger.warning("Using default: daily at 01:00")
        return {"type": "daily", "time": "01:00"}


def main():
    """Cron хуваарлагчийг эхлүүлэх үндсэн функц."""
    logger.info("=" * 60)
    logger.info("Starting Mongolian Bank Exchange Rate Crawler Scheduler")
    logger.info("=" * 60)
    logger.info(f"Cron Schedule: {config.CRON_SCHEDULE}")
    
    # Хуваарийг задлаж тохируулах
    schedule_params = parse_cron_schedule(config.CRON_SCHEDULE)
    
    if schedule_params["type"] == "daily":
        schedule.every().day.at(schedule_params["time"]).do(job)
        logger.info(f"Scheduled to run daily at {schedule_params['time']}")
    
    logger.info("Scheduler started. Press Ctrl+C to stop.")
    logger.info("=" * 60)
    
    # Эхлэхэд шууд ажиллуулах (сонголттой - хэрэггүй бол коммент хий)
    logger.info("Running initial crawl on startup...")
    job()
    
    # Хуваарлагчийг ажиллуулсан байлгах
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Минут бүр шалгах
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
    except Exception as e:
        logger.error(f"Scheduler error: {e}", exc_info=True)


if __name__ == "__main__":
    main()
