"""Sales endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query

from ..deps import get_proxy_client
from ..proxy_client import ProxyApiClient
from ..schemas import SalesRecord, SalesResponse


router = APIRouter(prefix="/sales", tags=["sales"])


@router.get("", response_model=SalesResponse)
async def get_sales(
    store_ids: List[int] = Query(..., description="Список ID магазинов"),
    start_date: str = Query(..., description="Начальная дата (YYYY-MM-DD)"),
    end_date: str = Query(..., description="Конечная дата (YYYY-MM-DD)"),
    proxy_client: ProxyApiClient = Depends(get_proxy_client),
) -> SalesResponse:
    if not store_ids:
        raise HTTPException(status_code=400, detail="store_ids must not be empty")

    data = await proxy_client.get_sales(store_ids=store_ids, start_date=start_date, end_date=end_date)
    records: List[SalesRecord] = []
    for row in data:
        try:
            order_date_raw = row.get("ORDER_DATE")
            if isinstance(order_date_raw, str):
                order_date = datetime.fromisoformat(order_date_raw)
            else:
                order_date = datetime.fromisoformat(str(order_date_raw))

            record = SalesRecord(
                store_name=str(row.get("STORE_NAME", "")),
                order_date=order_date,
                allcup=float(row.get("ALLCUP", 0) or 0),
                    packages_kg=float(row.get("PACKAGES_KG", 0) or 0),
                total_cash=float(row.get("TOTAL_CASH", 0) or 0),
            )
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=500, detail=f"Malformed sales record: {row}") from exc
        records.append(record)

    return SalesResponse(items=records, count=len(records))

