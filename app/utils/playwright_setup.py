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
        # Browsers might already be installed or we're in a restricted environment
        pass
