#!/usr/bin/env python
"""Утилита для проверки работы Proxy API коннектора."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from textwrap import indent

import pandas as pd
from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.logger_config import setup_logger  # noqa: E402
from src.proxy_api_connector import (  # noqa: E402
    ProxyApiAuthError,
    ProxyApiConnector,
    ProxyApiError,
    ProxyApiRateLimitError,
)


def mask_secret(value: str) -> str:
    if not value:
        return "—"
    if len(value) <= 8:
        return "***"
    return f"{value[:4]}***{value[-4:]}"


def main() -> int:
    load_dotenv(ROOT_DIR / "config" / "proxy_api.env")

    logger = setup_logger("proxy_api_test")
    logger.info("Запуск проверки Proxy API")

    api_url = os.getenv("PROXY_API_URL")
    primary_token = os.getenv("PROXY_API_TOKEN")
    fallback_token = os.getenv("PROXY_API_FALLBACK_TOKEN")
    tokens_env = os.getenv("PROXY_API_TOKENS")

    print("=" * 80)
    print("Проверка конфигурации Proxy API")
    print("=" * 80)
    print(f"URL: {api_url}")
    print(f"Primary token: {mask_secret(primary_token or '')}")
    print(f"Fallback token: {mask_secret(fallback_token or '')}")
    if tokens_env:
        print(f"Tokens (env list): {[mask_secret(t.strip()) for t in tokens_env.split(',') if t.strip()]}")
    print()

    if not api_url or not (primary_token or tokens_env):
        print("❌ Не настроены URL или токены. Отредактируйте config/proxy_api.env")
        return 1

    try:
        connector = ProxyApiConnector(
            api_url=api_url,
            primary_token=primary_token,
            fallback_token=fallback_token,
        )
    except ValueError as exc:
        print(f"❌ Ошибка инициализации коннектора: {exc}")
        return 1

    try:
        success, message = connector.test_connection()
    except ProxyApiError as exc:
        print(f"❌ Ошибка health check: {exc}")
        return 1

    status_text = "успех" if success else "ошибка"
    print(f"Health check ({status_text}): {message}")
    if not success:
        return 1

    print("\nСписок таблиц (первые 10):")
    try:
        tables = connector.get_tables()
    except ProxyApiError as exc:
        print(f"Не удалось получить список таблиц: {exc}")
        return 1
    print(indent("\n".join(tables[:10]), prefix="  "))

    print("\nТестовый SELECT (STORGRP, первые 5):")
    try:
        df_stores = connector.execute_query_to_dataframe(
            "SELECT FIRST 5 ID, NAME FROM STORGRP ORDER BY NAME"
        )
    except ProxyApiError as exc:
        print(f"Ошибка выполнения запроса: {exc}")
        return 1

    if df_stores.empty:
        print("Внимание: результат пустой")
    else:
        print(indent(df_stores.to_string(index=False), prefix="  "))

    print("\nПродажи кофе (демо запрос):")
    try:
        df_sales = connector.get_sales_data(store_ids=[27, 43], start_date="2025-01-01", end_date="2025-01-31")
    except ProxyApiRateLimitError as exc:
        print(f"Лимит запросов: {exc}")
    except ProxyApiAuthError as exc:
        print(f"Ошибка токена: {exc}")
        return 1
    except ProxyApiError as exc:
        print(f"Ошибка получения данных: {exc}")
        return 1
    else:
        print(f"Получено строк: {len(df_sales)}")
        if not df_sales.empty:
            preview_cols = [col for col in ["STORE_NAME", "ORDER_DATE", "ALLCUP", "PACKAGES_KG", "TOTAL_CASH"] if col in df_sales.columns]
            print(indent(df_sales.head(5)[preview_cols].to_string(index=False), prefix="  "))
        else:
            print("Внимание: за указанный период данные отсутствуют")

    connector.close()
    print("\nПроверка завершена успешно")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

