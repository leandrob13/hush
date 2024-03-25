import os

APP_PORT = os.getenv("APP_PORT", "8080")

APP_WORKERS = os.getenv("APP_WORKERS", 2)
