"""Health check endpoint."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from ..config import Settings, get_settings
from ..deps import get_proxy_client
from ..proxy_client import ProxyApiClient
from ..schemas import HealthResponse


router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=HealthResponse)
async def health_check(
    settings: Settings = Depends(get_settings),
    proxy_client: ProxyApiClient = Depends(get_proxy_client),
) -> HealthResponse:
    proxy_status = await proxy_client.health()
    return HealthResponse(
        status="ok",
        timestamp=datetime.now(timezone.utc),
        environment=settings.app_env,
        proxy_api=proxy_status,
    )

