"""Pydantic schemas for API responses."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    environment: str
    proxy_api: dict


class Store(BaseModel):
    id: int
    name: str


class SalesRecord(BaseModel):
    store_name: str
    order_date: datetime
    allcup: float
    packages_kg: float
    total_cash: float


class SalesResponse(BaseModel):
    items: List[SalesRecord]
    count: int

