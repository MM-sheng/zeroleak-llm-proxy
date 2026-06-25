"""Backtesting helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

import pandas as pd

from src.models import HistoricalVolatilityEstimate, estimate_historical_volatility
from src.backtest.synthetic_market_generator import SyntheticBTCMarket


@dataclass(frozen=True)
class TouchResolution:
    """Resolution result for a synthetic touch market."""

    market_id: str
    touched: bool
    touch_time_utc: datetime | None
    max_price: float
    min_price: float


def assert_no_future_data(
    data: pd.DataFrame,
    *,
    decision_time_utc: datetime,
    timestamp_column: str = "timestamp_utc",
) -> pd.DataFrame:
    """Return a copy only if all rows are strictly before the decision time."""
    decision_time = _coerce_utc(decision_time_utc)
    if not isinstance(data, pd.DataFrame):
        raise TypeError("data must be a pandas DataFrame")
    if timestamp_column not in data.columns:
        raise ValueError(f"data missing required timestamp column: {timestamp_column}")

    frame = data.copy()
    frame[timestamp_column] = pd.to_datetime(frame[timestamp_column], utc=True, errors="coerce")
    if frame[timestamp_column].isna().any():
        raise ValueError("data contains invalid timestamps")
    if (frame[timestamp_column] >= decision_time).any():
        raise ValueError("data contains rows at or after decision_time_utc")
    return frame


def estimate_prior_volatility(
    price_data: pd.DataFrame,
    *,
    decision_time_utc: datetime,
    window: int = 30,
    periods_per_year: int = 365,
) -> HistoricalVolatilityEstimate:
    """Estimate volatility using only rows before the decision time."""
    decision_time = _coerce_utc(decision_time_utc)

    frame = price_data.copy()
    if "timestamp_utc" not in frame.columns:
        raise ValueError("price_data missing required columns: ['timestamp_utc']")
    frame["timestamp_utc"] = pd.to_datetime(frame["timestamp_utc"], utc=True, errors="coerce")
    prior = frame.loc[frame["timestamp_utc"] < decision_time].copy()
    if prior.empty:
        raise ValueError("no prior price rows available before decision_time_utc")
    assert_no_future_data(prior, decision_time_utc=decision_time)
    return estimate_historical_volatility(prior, window=window, periods_per_year=periods_per_year)


def resolve_touch_market(
    price_data: pd.DataFrame,
    *,
    market: SyntheticBTCMarket,
) -> TouchResolution:
    """Resolve a synthetic touch market using future high/low after decision time."""
    if market.event_type != "touch":
        raise ValueError("resolve_touch_market only supports touch markets")
    frame = _validate_resolution_data(price_data)
    decision_time = _coerce_utc(market.decision_time_utc)
    deadline = _coerce_utc(market.deadline_utc)
    window = frame.loc[(frame["timestamp_utc"] > decision_time) & (frame["timestamp_utc"] <= deadline)].copy()
    if window.empty:
        raise ValueError("no resolution rows available after decision time and before deadline")

    max_price = float(window["high"].max())
    min_price = float(window["low"].min())
    if market.direction == "above":
        touched_rows = window.loc[window["high"] >= market.target_price]
    elif market.direction == "below":
        touched_rows = window.loc[window["low"] <= market.target_price]
    else:
        raise ValueError("market direction must be above or below")

    touch_time = None
    if not touched_rows.empty:
        touch_time = touched_rows.iloc[0]["timestamp_utc"].to_pydatetime()
    return TouchResolution(
        market_id=market.market_id,
        touched=not touched_rows.empty,
        touch_time_utc=touch_time,
        max_price=max_price,
        min_price=min_price,
    )


def _validate_resolution_data(price_data: pd.DataFrame) -> pd.DataFrame:
    """Validate OHLC data for touch market resolution."""
    if not isinstance(price_data, pd.DataFrame):
        raise TypeError("price_data must be a pandas DataFrame")
    missing = [column for column in ["timestamp_utc", "high", "low"] if column not in price_data.columns]
    if missing:
        raise ValueError(f"price_data missing required columns: {missing}")
    frame = price_data.loc[:, ["timestamp_utc", "high", "low"]].copy()
    frame["timestamp_utc"] = pd.to_datetime(frame["timestamp_utc"], utc=True, errors="coerce")
    frame["high"] = pd.to_numeric(frame["high"], errors="coerce")
    frame["low"] = pd.to_numeric(frame["low"], errors="coerce")
    frame = frame.sort_values("timestamp_utc").reset_index(drop=True)
    if frame.isna().any().any():
        raise ValueError("price_data contains invalid resolution values")
    return frame


def _coerce_utc(value: datetime) -> datetime:
    """Coerce a datetime to aware UTC."""
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)
