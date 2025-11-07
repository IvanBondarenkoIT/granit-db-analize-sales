"""Business logic for transforming Proxy API data."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Dict, Iterable, List, Tuple


def parse_date(value: str | datetime) -> datetime:
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value))


def aggregate_sales(records: Iterable[Dict[str, object]]) -> Dict[str, float]:
    total_sales = 0.0
    total_cups = 0.0
    total_packages = 0.0

    for row in records:
        total_sales += float(row.get("TOTAL_CASH", 0) or 0)
        total_cups += float(row.get("ALLCUP", 0) or 0)
        total_packages += float(row.get("PACKAGES_KG", 0) or 0)

    return {
        "total_sales": total_sales,
        "total_cups": total_cups,
        "total_packages": total_packages,
    }


def group_sales_by_store(records: Iterable[Dict[str, object]]) -> Dict[str, List[Dict[str, object]]]:
    grouped: Dict[str, List[Dict[str, object]]] = defaultdict(list)
    for row in records:
        store = str(row.get("STORE_NAME", ""))
        grouped[store].append(row)
    return grouped


def build_table_rows(records: Iterable[Dict[str, object]]) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for row in records:
        order_date = parse_date(row.get("ORDER_DATE"))
        rows.append(
            {
                "store_name": row.get("STORE_NAME", ""),
                "order_date": order_date,
                "allcup": float(row.get("ALLCUP", 0) or 0),
                "packages_kg": float(row.get("PACKAGES_KG", 0) or 0),
                "total_cash": float(row.get("TOTAL_CASH", 0) or 0),
            }
        )
    rows.sort(key=lambda r: (r["store_name"], r["order_date"]))
    return rows

