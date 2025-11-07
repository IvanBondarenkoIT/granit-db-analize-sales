"""Stores endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from ..deps import get_proxy_client
from ..proxy_client import ProxyApiClient
from ..schemas import Store


router = APIRouter(prefix="/stores", tags=["stores"])


@router.get("", response_model=list[Store])
async def list_stores(proxy_client: ProxyApiClient = Depends(get_proxy_client)) -> list[Store]:
    records = await proxy_client.get_stores()
    stores: list[Store] = []
    for record in records:
        try:
            store = Store(id=int(record["ID"]), name=str(record["NAME"]))
        except (KeyError, ValueError) as exc:
            raise ValueError(f"Malformed store record: {record}") from exc
        stores.append(store)
    return stores

