"""HTTP client for interacting with Firebird Proxy API."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Sequence

import requests
from requests import Response
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class ProxyApiError(Exception):
    pass


class ProxyApiAuthError(ProxyApiError):
    pass


class ProxyApiClient:
    def __init__(
        self,
        base_url: str,
        primary_token: str,
        fallback_token: Optional[str] = None,
        timeout: int = 30,
    ) -> None:
        if not base_url:
            raise ValueError("base_url is required")
        if not primary_token:
            raise ValueError("primary_token is required")

        self.base_url = base_url.rstrip("/")
        self.tokens: List[str] = [primary_token]
        if fallback_token:
            self.tokens.append(fallback_token)
        self._token_index = 0
        self.timeout = timeout

        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            backoff_factor=1,
            allowed_methods=["GET", "POST"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)

        self.session = requests.Session()
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.session.headers.update({"Content-Type": "application/json"})

    @property
    def current_token(self) -> str:
        return self.tokens[self._token_index]

    def _switch_token(self) -> bool:
        if len(self.tokens) <= 1:
            return False
        self._token_index = (self._token_index + 1) % len(self.tokens)
        return True

    def close(self) -> None:
        self.session.close()

    def _request(self, method: str, path: str, *, json: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"

        for attempt in range(len(self.tokens)):
            headers = {"Authorization": f"Bearer {self.current_token}"}
            response: Response = self.session.request(
                method=method,
                url=url,
                json=json,
                headers=headers,
                timeout=self.timeout,
            )

            if response.status_code == 401 and self._switch_token():
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
                raise ProxyApiError("Invalid JSON response from Proxy API") from exc

        raise ProxyApiAuthError("All tokens failed")

    # Public methods -----------------------------------------------------
    def health(self) -> Dict[str, Any]:
        return self._request("GET", "/api/health")

    def get_stores(self) -> List[Dict[str, Any]]:
        payload = self._request("GET", "/api/tables")
        tables = payload.get("tables", [])
        if "STORGRP" not in tables:
            return []
        query = "SELECT ID, NAME FROM STORGRP ORDER BY NAME"
        return self.execute_query(query)

    def execute_query(self, query: str, params: Optional[Sequence[Any]] = None) -> List[Dict[str, Any]]:
        body: Dict[str, Any] = {"query": query}
        if params is not None:
            body["params"] = list(params)
        payload = self._request("POST", "/api/query", json=body)
        if not payload.get("success"):
            raise ProxyApiError(payload.get("error", "Unknown query error"))
        return payload.get("data", [])

    def get_sales(
        self,
        store_ids: Sequence[int],
        start_date: str,
        end_date: str,
    ) -> List[Dict[str, Any]]:
        if not store_ids:
            return []
        placeholders = ",".join(["?"] * len(store_ids))
        params = list(store_ids) + [start_date, end_date]

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
              AND D.DAT_ >= ? AND D.DАТ_ <= ?
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
            GROUP BY stgp.NAME, D.ДАТ_
            ORDER BY stgp.NAME, D.ДАТ_
        """

        cups = self.execute_query(cups_query, params=params)
        packages = self.execute_query(packages_query, params=params)

        merged: Dict[tuple[str, str], Dict[str, Any]] = {}
        for row in cups:
            key = (str(row.get("STORE_NAME")), str(row.get("ORDER_DATE")))
            merged[key] = {
                "STORE_NAME": row.get("STORE_NAME"),
                "ORDER_DATE": row.get("ORDER_DATE"),
                "ALLCUP": row.get("ALLCUP", 0) or 0,
                "TOTAL_CASH": row.get("TOTAL_CASH", 0) or 0,
                "PACKAGES_KG": 0,
            }

        for row in packages:
            key = (str(row.get("STORE_NAME")), str(row.get("ORDER_DATE")))
            merged.setdefault(
                key,
                {
                    "STORE_NAME": row.get("STORE_NAME"),
                    "ORDER_DATE": row.get("ORDER_DATE"),
                    "ALLCUP": 0,
                    "TOTAL_CASH": 0,
                    "PACKAGES_KG": 0,
                },
            )
            merged[key]["PACKAGES_KG"] = row.get("PACKAGES_KG", 0) or 0

        return list(merged.values())

