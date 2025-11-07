"""Proxy API connector for safe READ-ONLY access to Firebird via REST."""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import pandas as pd
import requests
from dotenv import load_dotenv
from requests import Response
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# Загружаем локальные секреты (если файл существует)
load_dotenv("config/proxy_api.env", override=False)


class ProxyApiError(Exception):
    """Базовое исключение для ошибок Proxy API."""


class ProxyApiAuthError(ProxyApiError):
    """Ошибка аутентификации."""


class ProxyApiRateLimitError(ProxyApiError):
    """Ошибка превышения лимита запросов."""


class ProxyApiConnector:
    """Клиент для взаимодействия с Firebird Database Proxy API."""

    _STATUS_RETRY = {429, 500, 502, 503, 504}

    def __init__(
        self,
        api_url: Optional[str] = None,
        primary_token: Optional[str] = None,
        fallback_token: Optional[str] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.logger = logging.getLogger(__name__)

        self.api_url = (api_url or os.getenv("PROXY_API_URL", "")).rstrip("/")
        if not self.api_url:
            raise ValueError("PROXY_API_URL is not configured")

        tokens: List[str] = []
        env_tokens = os.getenv("PROXY_API_TOKENS", "")
        if env_tokens:
            tokens.extend(token.strip() for token in env_tokens.split(",") if token.strip())

        for candidate in (primary_token, os.getenv("PROXY_API_TOKEN"), fallback_token, os.getenv("PROXY_API_FALLBACK_TOKEN")):
            if candidate and candidate not in tokens:
                tokens.append(candidate)

        self.tokens: List[str] = [token for token in tokens if token]
        if not self.tokens:
            raise ValueError("No API tokens provided for Proxy API connector")

        self._token_index = 0

        self.timeout = timeout or int(os.getenv("PROXY_API_TIMEOUT", "30"))
        self.max_retries = max_retries or int(os.getenv("PROXY_API_MAX_RETRIES", "3"))

        self.session = session or requests.Session()
        retry_strategy = Retry(
            total=self.max_retries,
            status_forcelist=self._STATUS_RETRY,
            backoff_factor=1,
            allowed_methods=("GET", "POST"),
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.session.headers.update({"Content-Type": "application/json"})

        self.logger.info("ProxyApiConnector initialised. URL=%s", self.api_url)

    # ------------------------------------------------------------------
    # Low-level helpers
    # ------------------------------------------------------------------
    def _masked_token(self, token: str) -> str:
        if len(token) <= 8:
            return "***hidden***"
        return f"{token[:4]}***{token[-4:]}"

    @property
    def current_token(self) -> str:
        return self.tokens[self._token_index]

    def _switch_token(self) -> bool:
        if len(self.tokens) <= 1:
            return False
        self._token_index = (self._token_index + 1) % len(self.tokens)
        self.logger.warning(
            "Switching to fallback token (%s)", self._masked_token(self.current_token)
        )
        return True

    def _request(self, method: str, path: str, *, json: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.api_url}{path}"

        for attempt in range(len(self.tokens)):
            headers = {"Authorization": f"Bearer {self.current_token}"}
            try:
                response: Response = self.session.request(
                    method=method,
                    url=url,
                    json=json,
                    headers=headers,
                    timeout=self.timeout,
                )
            except requests.RequestException as exc:
                raise ProxyApiError(f"Request to {url} failed: {exc}") from exc

            if response.status_code == 401:
                masked = self._masked_token(self.current_token)
                self.logger.warning("Proxy API returned 401 for token %s", masked)
                if self._switch_token():
                    continue
                raise ProxyApiAuthError("Authentication failed for Proxy API")

            if response.status_code == 429:
                raise ProxyApiRateLimitError("Proxy API rate limit exceeded (429)")

            if response.status_code >= 400:
                try:
                    payload = response.json()
                except ValueError:
                    payload = response.text
                raise ProxyApiError(f"Proxy API error {response.status_code}: {payload}")

            try:
                return response.json()
            except ValueError as exc:
                raise ProxyApiError("Invalid JSON response from Proxy API") from exc

        raise ProxyApiAuthError("All Proxy API tokens failed")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def close(self) -> None:
        if self.session:
            self.session.close()

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass

    def test_connection(self) -> Tuple[bool, str]:
        """Проверка доступности API и соединения с БД."""

        try:
            payload = self._request("GET", "/api/health")
        except ProxyApiError as exc:
            return False, str(exc)

        status = payload.get("status")
        database_connected = payload.get("database_connected")
        if status == "healthy" and database_connected:
            return True, "Proxy API is healthy and database connection is available"
        return False, f"Health check returned unexpected payload: {payload}"

    def execute_query_to_dataframe(
        self, query: str, params: Optional[Sequence[Any]] = None
    ) -> pd.DataFrame:
        """Выполняет SELECT запрос и возвращает DataFrame."""

        payload = {"query": query}
        if params is not None:
            payload["params"] = list(params)

        response = self._request("POST", "/api/query", json=payload)

        if not response.get("success"):
            raise ProxyApiError(response.get("error") or "Unknown query error")

        data = response.get("data") or []
        if not data:
            return pd.DataFrame()
        return pd.DataFrame(data)

    # Convenience helpers -------------------------------------------------
    def get_tables(self) -> List[str]:
        response = self._request("GET", "/api/tables")
        return response.get("tables", [])

    def get_stores_dataframe(self) -> pd.DataFrame:
        query = "SELECT ID, NAME FROM STORGRP ORDER BY NAME"
        df = self.execute_query_to_dataframe(query)
        if df.empty:
            return pd.DataFrame(columns=["ID", "NAME"])
        return df

    def get_sales_data(
        self,
        store_ids: Sequence[int],
        start_date: str,
        end_date: str,
    ) -> pd.DataFrame:
        if not store_ids:
            raise ValueError("store_ids must not be empty")

        placeholders = ",".join(["?"] * len(store_ids))
        params_stores: List[Any] = list(store_ids)

        base_params = params_stores + [start_date, end_date]

        cups_query = f"""
            SELECT 
                stgp.NAME AS STORE_NAME,
                D.DAT_ AS ORDER_DATE,
                COUNT(*) AS ALLCUP,
                SUM(D.SUMMA) AS TOTAL_CASH
            FROM STORZAKAZDT D
            JOIN STORGRP stgp ON D.STORGRPID = stgp.ID
            WHERE D.STORGRPID IN ({placeholders})
              AND D.CSDTKTHBID IN ('1', '2', '3', '5')
              AND D.DAT_ >= ? AND D.DAT_ <= ?
            GROUP BY stgp.NAME, D.DAT_
            ORDER BY stgp.NAME, D.DAT_
        """

        packages_query = f"""
            SELECT
                stgp.NAME AS STORE_NAME,
                D.DAT_ AS ORDER_DATE,
                SUM(GD.SOURCE) AS PACKAGES_KG
            FROM STORZAKAZDT D
            JOIN STORZDTGDS GD ON D.ID = GD.SZID
            JOIN GOODS G ON GD.GODSId = G.ID
            JOIN STORGRP stgp ON D.STORGRPID = stgp.ID
            LEFT JOIN GOODSGROUPS GG ON G.OWNER = GG.ID
            WHERE D.STORGRPID IN ({placeholders})
              AND D.CSDTKTHBID IN ('1', '2', '3', '5')
              AND D.DAT_ >= ? AND D.DAT_ <= ?
              AND (
                    (
                        (G.NAME LIKE '%250 g%' OR G.NAME LIKE '%250г%' OR
                         G.NAME LIKE '%500 g%' OR G.NAME LIKE '%500г%' OR
                         G.NAME LIKE '%1 kg%' OR G.NAME LIKE '%1кг%' OR
                         G.NAME LIKE '%200 g%' OR G.NAME LIKE '%200г%' OR
                         G.NAME LIKE '%125 g%' OR G.NAME LIKE '%125г%' OR
                         G.NAME LIKE '%80 g%' OR G.NAME LIKE '%80г%' OR
                         G.NAME LIKE '%0.25%' OR G.NAME LIKE '%0.5%' OR
                         G.NAME LIKE '%0.2%' OR G.NAME LIKE '%0.125%' OR
                         G.NAME LIKE '%0.08%')
                        AND (G.NAME LIKE '%Coffee%' OR G.NAME LIKE '%кофе%' OR G.NAME LIKE '%Кофе%' OR G.NAME LIKE '%Blaser%')
                    )
                    OR (GG.NAME LIKE '%Caotina swiss chocolate drink (package)%')
              )
            GROUP BY stgp.NAME, D.DAT_
            ORDER BY stgp.NAME, D.DAT_
        """

        df_cups = self.execute_query_to_dataframe(cups_query, base_params)
        df_packages = self.execute_query_to_dataframe(packages_query, base_params)

        if df_cups.empty and df_packages.empty:
            return pd.DataFrame(
                columns=["STORE_NAME", "ORDER_DATE", "ALLCUP", "PACKAGES_KG", "TOTAL_CASH"]
            )

        df = df_cups.merge(
            df_packages,
            on=["STORE_NAME", "ORDER_DATE"],
            how="left",
        )
        df["PACKAGES_KG"] = df.get("PACKAGES_KG", 0).fillna(0)
        return df


__all__ = ["ProxyApiConnector", "ProxyApiError", "ProxyApiAuthError", "ProxyApiRateLimitError"]

