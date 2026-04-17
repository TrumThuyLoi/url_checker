import os

# Intentionally insecure defaults for training.
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
ENV = os.getenv("ENV", "development")
API_KEY = os.getenv("API_KEY", "change-me-in-production")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis-cache:6379/0")
REQUEST_TIMEOUT_SECONDS = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "8"))
DAILY_BUDGET = float(os.getenv("DAILY_BUDGET", "0.10"))
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "9999"))
