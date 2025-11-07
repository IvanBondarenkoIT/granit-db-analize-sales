"""Async client for communicating with the Firebird Proxy API."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import httpx


class ProxyApiError(Exception):
    """Base exception for proxy API errors."""


class ProxyApiAuthError(ProxyApiError):
    pass


class ProxyApiClient:
    def __init__(
        self,
        base_url: str,
        primary_token: Optional[str] = None,
        fallback_token: Optional[str] = None,
        timeout: int = 30,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        tokens: List[str] = []
        if primary_token:
            tokens.append(primary_token)
        if fallback_token:
            tokens.append(fallback_token)
        self.tokens = tokens
        if not self.tokens:
            raise ValueError("No API token provided")
        self._token_index = 0
        self.timeout = timeout
        self._client = httpx.AsyncClient(timeout=timeout)

    @property
    def current_token(self) -> str:
        return self.tokens[self._token_index]

    def _switch_token(self) -> bool:
        if len(self.tokens) <= 1:
            return False
        self._token_index = (self._token_index + 1) % len(self.tokens)
        return True

    async def close(self) -> None:
        await self._client.aclose()

    async def _request(self, method: str, path: str, *, json: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        attempts = 0
        max_attempts = len(self.tokens)

        while attempts < max_attempts:
            headers = {"Authorization": f"Bearer {self.current_token}"}
            response = await self._client.request(method, url, json=json, headers=headers)

            if response.status_code == 401 and self._switch_token():
                attempts += 1
                continue

            if response.status_code == 401:
                raise ProxyApiAuthError("Authentication with Proxy API failed")

            if response.status_code >= 400:
                try:
                    payload = response.json()
                except ValueError:
                    payload = response.text
                raise ProxyApiError(f"Proxy API error {response.status_code}: {payload}")

            try:
                return response.json()
            except ValueError as exc:
                raise ProxyApiError("Invalid JSON from Proxy API") from exc

        raise ProxyApiAuthError("All Proxy API tokens failed")

    async def health(self) -> Dict[str, Any]:
        return await self._request("GET", "/api/health")

    async def get_tables(self) -> List[str]:
        payload = await self._request("GET", "/api/tables")
        return payload.get("tables", [])

    async def execute_query(self, query: str, params: Optional[Sequence[Any]] = None) -> List[Dict[str, Any]]:
        body: Dict[str, Any] = {"query": query}
        if params is not None:
            body["params"] = list(params)
        payload = await self._request("POST", "/api/query", json=body)
        if not payload.get("success"):
            raise ProxyApiError(payload.get("error", "Unknown query error"))
        return payload.get("data", [])

    async def get_stores(self) -> List[Dict[str, Any]]:
        query = "SELECT ID, NAME FROM STORGRP ORDER BY NAME"
        return await self.execute_query(query)

    async def get_sales(
        self,
        store_ids: Sequence[int],
        start_date: str,
        end_date: str,
    ) -> List[Dict[str, Any]]:
        placeholders = ",".join(["?"] * len(store_ids))
        params: List[Any] = list(store_ids) + [start_date, end_date]

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

        cups = await self.execute_query(cups_query, params=params)
        packages = await self.execute_query(packages_query, params=params)
        return self._merge_sales(cups, packages)

    def _merge_sales(
        self,
        cups: List[Dict[str, Any]],
        packages: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        merged: Dict[Tuple[str, str], Dict[str, Any]] = {}

        for row in cups:
            key = (str(row.get("STORE_NAME")), str(row.get("ORDER_DATE")))
            merged[key] = {
                "STORE_NAME": row.get("STORE_NAME"),
                "ORDER_DATE": row.get("ORDER_DATE"),
                "ALLCUP": row.get("ALLCUP", 0),
                "TOTAL_CASH": row.get("TOTAL_CASH", 0),
                "PACKAGES_KG": 0,
            }

        for row in packages:
            key = (str(row.get("STORE_NAME")), str(row.get("ORDER_DATE")))
            record = merged.setdefault(
                key,
                {
                    "STORE_NAME": row.get("STORE_NAME"),
                    "ORDER_DATE": row.get("ORDER_DATE"),
                    "ALLCUP": 0,
                    "TOTAL_CASH": 0,
                    "PACKAGES_KG": 0,
                },
            )
            record["PACKAGES_KG"] = row.get("PACKAGES_KG", 0)

        return list(merged.values())

