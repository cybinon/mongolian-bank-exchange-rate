#!/usr/bin/env python3
"""Backfill historical exchange rate data.

Usage:
    python scripts/backfill.py                  # 2026-01-01 to today
    python scripts/backfill.py 2026-01-01       # From date to today
    python scripts/backfill.py 2026-01-01 2026-01-15  # Date range
"""

import sys
from datetime import date, timedelta

from app.services.scraper import ScraperService
from app.utils.logger import logger


def backfill(start: date, end: date):
    total = (end - start).days + 1
    logger.info(f"Backfill: {start} to {end} ({total} days)")

    current = start
    count = 0
    while current <= end:
        count += 1
        logger.info(f"[{count}/{total}] {current}")
        try:
            ScraperService(date=current.isoformat()).run_all()
        except Exception as e:
            logger.error(f"Failed {current}: {e}")
        current += timedelta(days=1)

    logger.info(f"Backfill done: {count} days")


def main():
    start = date(2026, 1, 1)
    end = date.today()

    if len(sys.argv) >= 2:
        start = date.fromisoformat(sys.argv[1])
    if len(sys.argv) >= 3:
        end = date.fromisoformat(sys.argv[2])

    if start > end:
        logger.error("Start date must be <= end date")
        sys.exit(1)

    backfill(start, end)


if __name__ == "__main__":
    main()
