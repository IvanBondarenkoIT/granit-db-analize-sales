"""Application configuration for the Flask monolith."""

from __future__ import annotations

import os
from functools import lru_cache

from dotenv import load_dotenv


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.path.join(BASE_DIR, "env")


def _load_env() -> None:
    if os.path.exists(ENV_FILE):
        load_dotenv(ENV_FILE)
    else:
        load_dotenv()  # fallback: load from .env in root if present


_load_env()


class Settings:
    """Application settings lazily loaded from environment variables."""

    def __init__(self) -> None:
        self.secret_key: str = os.getenv("SECRET_KEY", "change-me")
        self.proxy_api_url: str = os.getenv("PROXY_API_URL", "http://localhost:8000")
        self.proxy_primary_token: str | None = os.getenv("PROXY_PRIMARY_TOKEN")
        self.proxy_fallback_token: str | None = os.getenv("PROXY_FALLBACK_TOKEN")
        self.proxy_timeout: int = int(os.getenv("PROXY_TIMEOUT", "30"))

        if not self.secret_key or self.secret_key == "change-me":
            raise RuntimeError("SECRET_KEY is not configured")
        if not self.proxy_api_url:
            raise RuntimeError("PROXY_API_URL is not configured")
        if not self.proxy_primary_token:
            raise RuntimeError("PROXY_PRIMARY_TOKEN is not configured")


@lru_cache()
def get_settings() -> Settings:
    return Settings()

