"""FastAPI dependencies."""

from __future__ import annotations

from functools import lru_cache

from .config import Settings, get_settings
from .proxy_client import ProxyApiClient


@lru_cache()
def get_proxy_client() -> ProxyApiClient:
    settings: Settings = get_settings()
    return ProxyApiClient(
        base_url=str(settings.proxy_api_url),
        primary_token=settings.proxy_primary_token or None,
        fallback_token=settings.proxy_fallback_token or None,
        timeout=settings.proxy_timeout,
    )


async def close_proxy_client() -> None:
    client = get_proxy_client()
    await client.close()

