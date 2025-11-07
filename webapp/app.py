from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import List, Optional

from flask import Flask, render_template, request

from config import get_settings
from proxy_client import ProxyApiClient, ProxyApiError
from services.analytics import aggregate_sales, build_table_rows

settings = get_settings()

app = Flask(__name__)
app.config["SECRET_KEY"] = settings.secret_key

client = ProxyApiClient(
    base_url=settings.proxy_api_url,
    primary_token=settings.proxy_primary_token,
    fallback_token=settings.proxy_fallback_token,
    timeout=settings.proxy_timeout,
)

logger = logging.getLogger(__name__)


def _parse_int(value: str | None) -> Optional[int]:
    if not value:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def _default_dates() -> tuple[str, str]:
    today = datetime.now(timezone.utc).date()
    start = today.replace(day=1)
    return start.isoformat(), today.isoformat()


@app.route("/")
def dashboard():
    start_date, end_date = _default_dates()

    try:
        health = client.health()
        stores = client.get_stores()
        sales = client.get_sales([store["ID"] for store in stores], start_date, end_date)
    except ProxyApiError as exc:
        logger.error("Proxy API error: %s", exc)
        health = None
        stores = []
        sales = []

    rows = build_table_rows(sales)
    totals = aggregate_sales(sales)

    return render_template(
        "dashboard.html",
        stores_count=len(stores),
        totals=totals,
        rows=rows,
        period={"start": start_date, "end": end_date},
        health=health,
    )


@app.route("/sales")
def sales_table():
    start_date = request.args.get("start_date") or _default_dates()[0]
    end_date = request.args.get("end_date") or _default_dates()[1]
    store_filter = _parse_int(request.args.get("store"))
    sort = request.args.get("sort", "date")

    try:
        stores = client.get_stores()
        store_ids: List[int]
        if store_filter:
            store_ids = [store_filter]
        else:
            store_ids = [int(store["ID"]) for store in stores]

        sales = client.get_sales(store_ids, start_date, end_date)
    except ProxyApiError as exc:
        logger.error("Proxy API error: %s", exc)
        stores = []
        sales = []

    rows = build_table_rows(sales)

    if sort == "store":
        rows.sort(key=lambda r: (r["store_name"], r["order_date"]))
    elif sort == "sum":
        rows.sort(key=lambda r: r["total_cash"], reverse=True)
    else:
        rows.sort(key=lambda r: r["order_date"], reverse=True)

    return render_template(
        "sales_table.html",
        rows=rows,
        stores=[{"id": int(store["ID"]), "name": store["NAME"]} for store in stores],
        filters={
            "start_date": start_date,
            "end_date": end_date,
            "store": store_filter,
            "sort": sort,
        },
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(host="0.0.0.0", port=8000)
