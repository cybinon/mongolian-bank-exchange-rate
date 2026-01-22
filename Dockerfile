# Mongolian bank exchange-rate API - Docker image
FROM python:3.11-slim AS base

# Set working directory
WORKDIR /app

# Base environment flags
ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Install Python dependencies
COPY requirements.txt .
RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Install Playwright and required system dependencies in one step
RUN playwright install --with-deps chromium

# Copy application code
COPY . .

# ============ Test Stage ============
FROM base AS test

# Run tests
RUN pytest --cov=app --cov-report=term-missing -v

# ============ Production Stage ============
FROM base AS production

# Run as non-root user
RUN adduser --disabled-password --gecos "" appuser \
    && mkdir -p /app/logs \
    && chown -R appuser:appuser /app /ms-playwright
USER appuser

# Expose port
EXPOSE 8000

# Healthcheck using the /health endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=5)" || exit 1

# Default command
CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
