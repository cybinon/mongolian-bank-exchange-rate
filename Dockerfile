# Монгол банкны ханшийн API - Docker хувилбар
FROM python:3.11-slim

# Ажлын хавтас тохируулах
WORKDIR /app

# Систем хамаарлуудыг суулгах (Playwright-д шаардлагатай)
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libwayland-client0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Python хамаарлуудыг суулгах
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Playwright хөтчүүдийг суулгах
RUN playwright install chromium
RUN playwright install-deps chromium

# Апликейшны кодыг хуулах
COPY . .

# Портыг задлах
EXPOSE 8000

# Эрүүл мэндийн шалгалт
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/', timeout=5)" || exit 1

# Үндсэн команд
CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
