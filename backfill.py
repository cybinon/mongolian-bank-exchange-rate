#!/usr/bin/env python3
"""
Backfill historical exchange rate data.

Usage:
    python backfill.py                    # Backfill from 2026-01-01 to today
    python backfill.py 2026-01-01         # Backfill from specific date to today
    python backfill.py 2026-01-01 2026-01-15  # Backfill specific date range
"""

import sys
from datetime import date, timedelta

from app.services.scraper_service import ScraperService
from app.utils.logger import get_logger

logger = get_logger("backfill")


def backfill(start_date: date, end_date: date):
    """Backfill exchange rates for a date range."""
    current_date = start_date
    total_days = (end_date - start_date).days + 1
    
    logger.info(f"Starting backfill from {start_date} to {end_date} ({total_days} days)")
    
    day_count = 0
    while current_date <= end_date:
        day_count += 1
        date_str = current_date.isoformat()
        logger.info(f"[{day_count}/{total_days}] Processing {date_str}")
        
        try:
            service = ScraperService(date=date_str)
            service.run_crawlers()
        except Exception as e:
            logger.exception(f"Failed to process {date_str}: {e}")
        
        current_date += timedelta(days=1)
    
    logger.info(f"Backfill completed: processed {day_count} days")


def main():
    # Default: from 2026-01-01 to today
    start_date = date(2026, 1, 1)
    end_date = date.today()
    
    if len(sys.argv) >= 2:
        start_date = date.fromisoformat(sys.argv[1])
    
    if len(sys.argv) >= 3:
        end_date = date.fromisoformat(sys.argv[2])
    
    if start_date > end_date:
        logger.error("Start date must be before or equal to end date")
        sys.exit(1)
    
    backfill(start_date, end_date)


if __name__ == "__main__":
    main()
