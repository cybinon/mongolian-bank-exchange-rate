import subprocess
import sys


def ensure_playwright_browsers():
    """Install Playwright browsers if not already installed."""
    try:
        subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError:
        # Browsers already installed or restricted environment
        pass
