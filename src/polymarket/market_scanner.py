"""Read-only Polymarket market scanning helpers."""

from __future__ import annotations

import json
from collections.abc import Iterable
from datetime import datetime, timezone
from typing import Any

from src.polymarket.gamma_client import GammaClient


DEFAULT_BTC_KEYWORDS = ("bitcoin", "btc")
SEARCH_FIELDS = ("question", "title", "slug", "description")
MARKET_SCHEMA = (
    "market_id",
    "question",
    "slug",
    "outcomes",
    "outcome_prices",
    "yes_price",
    "no_price",
    "volume",
    "liquidity",
    "end_date_utc",
    "active",
    "closed",
    "raw",
)


def search_btc_markets(
    client: GammaClient | None = None,
    *,
    keywords: Iterable[str] = DEFAULT_BTC_KEYWORDS,
    **gamma_params: Any,
) -> list[dict[str, Any]]:
    """Return raw Gamma markets whose text appears BTC-related.

    This task intentionally performs only read-only discovery. Market schema
    normalization, active/closed/liquidity filtering, and YES/NO price
    extraction are handled by later Phase 2 tasks.
    """
    gamma_client = client or GammaClient()
    normalized_keywords = _normalize_keywords(keywords)
    markets = gamma_client.get_markets(**gamma_params)
    return [market for market in markets if _market_matches_keywords(market, normalized_keywords)]


def standardize_market(raw_market: dict[str, Any]) -> dict[str, Any]:
    """Normalize one raw Gamma market to the project market schema.

    This does not filter markets and does not infer YES/NO prices from outcome
    arrays. Those behaviors are owned by later Phase 2 tasks.
    """
    if not isinstance(raw_market, dict):
        raise TypeError("raw_market must be a dictionary")

    outcomes = _coerce_sequence(_first_present(raw_market, "outcomes"))
    outcome_prices = _coerce_sequence(_first_present(raw_market, "outcomePrices", "outcome_prices"))
    explicit_yes_price = _coerce_probability(_first_present(raw_market, "yes_price", "yesPrice"))
    explicit_no_price = _coerce_probability(_first_present(raw_market, "no_price", "noPrice"))

    standardized = {
        "market_id": _first_present(raw_market, "id", "market_id", "conditionId", "condition_id"),
        "question": _first_present(raw_market, "question", "title"),
        "slug": _first_present(raw_market, "slug"),
        "outcomes": outcomes,
        "outcome_prices": outcome_prices,
        "yes_price": explicit_yes_price
        if explicit_yes_price is not None
        else _extract_outcome_price("yes", outcomes, outcome_prices),
        "no_price": explicit_no_price
        if explicit_no_price is not None
        else _extract_outcome_price("no", outcomes, outcome_prices),
        "volume": _coerce_float(_first_present(raw_market, "volume", "volumeNum")),
        "liquidity": _coerce_float(_first_present(raw_market, "liquidity", "liquidityNum")),
        "end_date_utc": _coerce_utc_datetime(
            _first_present(raw_market, "endDate", "end_date", "endDateIso", "end_date_utc")
        ),
        "active": _coerce_bool(_first_present(raw_market, "active")),
        "closed": _coerce_bool(_first_present(raw_market, "closed")),
        "raw": raw_market,
    }
    return {field: standardized[field] for field in MARKET_SCHEMA}


def standardize_markets(raw_markets: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Normalize multiple raw Gamma markets to the project market schema."""
    return [standardize_market(raw_market) for raw_market in raw_markets]


def filter_tradeable_markets(
    markets: Iterable[dict[str, Any]],
    *,
    min_liquidity: float = 0.0,
) -> list[dict[str, Any]]:
    """Keep markets that are active, open, and above the liquidity threshold.

    Unknown ``active``, ``closed``, or ``liquidity`` values are treated as not
    tradeable. This function does not size positions and does not imply that a
    market should be traded.
    """
    if min_liquidity < 0:
        raise ValueError("min_liquidity must be non-negative")
    return [
        market
        for market in markets
        if _is_tradeable_market(market, min_liquidity=min_liquidity)
    ]


def _normalize_keywords(keywords: Iterable[str]) -> tuple[str, ...]:
    """Normalize and validate BTC search keywords."""
    normalized = tuple(
        keyword.strip().lower()
        for keyword in keywords
        if isinstance(keyword, str) and keyword.strip()
    )
    if not normalized:
        raise ValueError("at least one non-empty keyword is required")
    return normalized


def _market_matches_keywords(market: dict[str, Any], keywords: tuple[str, ...]) -> bool:
    """Return whether any configured keyword appears in common market text fields."""
    if not isinstance(market, dict):
        return False
    searchable_text = " ".join(
        str(market.get(field, "")).lower()
        for field in SEARCH_FIELDS
    )
    return any(keyword in searchable_text for keyword in keywords)


def _is_tradeable_market(market: dict[str, Any], *, min_liquidity: float) -> bool:
    """Return whether a standardized market passes basic availability filters."""
    if not isinstance(market, dict):
        return False
    if market.get("active") is not True:
        return False
    if market.get("closed") is not False:
        return False
    liquidity = _coerce_float(market.get("liquidity"))
    if liquidity is None:
        return False
    return liquidity >= min_liquidity


def _first_present(source: dict[str, Any], *keys: str) -> Any:
    """Return the first present non-None value from a raw market."""
    for key in keys:
        if key in source and source[key] is not None:
            return source[key]
    return None


def _coerce_sequence(value: Any) -> list[Any]:
    """Coerce Gamma list-like or JSON-string values into a list."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return [value]
        return parsed if isinstance(parsed, list) else [parsed]
    return [value]


def _coerce_float(value: Any) -> float | None:
    """Coerce numeric Gamma values to float, preserving unknowns as None."""
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _coerce_probability(value: Any) -> float | None:
    """Coerce a market price/probability only when it is inside the 0-1 range."""
    number = _coerce_float(value)
    if number is None:
        return None
    if 0.0 <= number <= 1.0:
        return number
    return None


def _extract_outcome_price(
    outcome_name: str,
    outcomes: list[Any],
    outcome_prices: list[Any],
) -> float | None:
    """Extract a YES or NO price by matching outcome labels to price indexes."""
    target = outcome_name.strip().lower()
    for index, outcome in enumerate(outcomes):
        if str(outcome).strip().lower() != target:
            continue
        if index >= len(outcome_prices):
            return None
        return _coerce_probability(outcome_prices[index])
    return None


def _coerce_bool(value: Any) -> bool | None:
    """Coerce common raw bool representations without inventing unknown values."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes"}:
            return True
        if normalized in {"false", "0", "no"}:
            return False
    if isinstance(value, int) and value in {0, 1}:
        return bool(value)
    return None


def _coerce_utc_datetime(value: Any) -> datetime | None:
    """Coerce common Gamma datetime strings to UTC-aware datetimes."""
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
    if isinstance(value, str):
        normalized = value.strip()
        if normalized.endswith("Z"):
            normalized = f"{normalized[:-1]}+00:00"
        try:
            parsed = datetime.fromisoformat(normalized)
        except ValueError:
            return None
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    return None
