"""Read-only client for Polymarket Gamma metadata endpoints."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urljoin

import requests


DEFAULT_GAMMA_BASE_URL = "https://gamma-api.polymarket.com"


class GammaClientError(RuntimeError):
    """Raised when the Gamma API cannot return usable market metadata."""


@dataclass
class GammaClient:
    """Small read-only wrapper around Polymarket Gamma metadata endpoints."""

    base_url: str = DEFAULT_GAMMA_BASE_URL
    timeout_seconds: int = 20
    session: requests.Session = field(default_factory=requests.Session)

    def __post_init__(self) -> None:
        """Validate client configuration."""
        if not self.base_url or not self.base_url.strip():
            raise ValueError("base_url must be a non-empty string")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self.base_url = self.base_url.rstrip("/")

    def get_markets(self, **params: Any) -> list[dict[str, Any]]:
        """Fetch market metadata from the read-only Gamma ``/markets`` endpoint."""
        payload = self._get_json("/markets", params=params)
        if isinstance(payload, list):
            return payload
        if isinstance(payload, dict) and isinstance(payload.get("markets"), list):
            return payload["markets"]
        raise GammaClientError("Gamma /markets response was not a market list")

    def get_market(self, market_id: str | int) -> dict[str, Any]:
        """Fetch one market by Gamma market identifier."""
        if market_id is None or str(market_id).strip() == "":
            raise ValueError("market_id must be non-empty")
        payload = self._get_json(f"/markets/{market_id}", params=None)
        if not isinstance(payload, dict):
            raise GammaClientError("Gamma market response was not an object")
        return payload

    def _get_json(self, path: str, *, params: dict[str, Any] | None) -> Any:
        """Perform a read-only GET request and return decoded JSON."""
        url = urljoin(f"{self.base_url}/", path.lstrip("/"))
        try:
            response = self.session.get(url, params=params, timeout=self.timeout_seconds)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            raise GammaClientError(f"Gamma API request failed: {exc}") from exc
        except ValueError as exc:
            raise GammaClientError("Gamma API response was not valid JSON") from exc
