"""Historical volatility model for BTC probability inputs."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class HistoricalVolatilityEstimate:
    """Trailing historical volatility estimate from BTC close prices."""

    annualized_volatility: float
    annualized_mean_log_return: float
    window: int
    periods_per_year: int
    observations: int
    latest_close: float
    as_of_utc: datetime
    warnings: tuple[str, ...] = field(default_factory=tuple)


def estimate_historical_volatility(
    data: pd.DataFrame,
    *,
    window: int = 30,
    periods_per_year: int = 365,
) -> HistoricalVolatilityEstimate:
    """Estimate trailing annualized volatility from historical BTC closes.

    The estimate uses only the final ``window`` log returns available in
    ``data``. It does not fetch data, infer future values, or use look-ahead
    information.
    """
    frame = _validate_input(data, window=window, periods_per_year=periods_per_year)
    closes = frame["close"].astype(float)
    log_returns = np.log(closes / closes.shift(1)).dropna()
    trailing_returns = log_returns.tail(window)
    warnings: list[str] = []

    annualized_volatility = float(trailing_returns.std(ddof=1) * np.sqrt(periods_per_year))
    if annualized_volatility == 0.0:
        warnings.append("zero_volatility")

    annualized_mean_log_return = float(trailing_returns.mean() * periods_per_year)
    as_of = frame.iloc[-1]["timestamp_utc"].to_pydatetime()
    if as_of.tzinfo is None:
        as_of = as_of.replace(tzinfo=timezone.utc)
    else:
        as_of = as_of.astimezone(timezone.utc)

    return HistoricalVolatilityEstimate(
        annualized_volatility=annualized_volatility,
        annualized_mean_log_return=annualized_mean_log_return,
        window=window,
        periods_per_year=periods_per_year,
        observations=len(trailing_returns),
        latest_close=float(closes.iloc[-1]),
        as_of_utc=as_of,
        warnings=tuple(warnings),
    )


def _validate_input(data: pd.DataFrame, *, window: int, periods_per_year: int) -> pd.DataFrame:
    """Validate model input and return a sorted canonical frame."""
    if window < 2:
        raise ValueError("window must be at least 2")
    if periods_per_year <= 0:
        raise ValueError("periods_per_year must be positive")
    if not isinstance(data, pd.DataFrame):
        raise TypeError("historical volatility input must be a pandas DataFrame")

    missing = [column for column in ["timestamp_utc", "close"] if column not in data.columns]
    if missing:
        raise ValueError(f"historical volatility input missing required columns: {missing}")
    if data.empty:
        raise ValueError("historical volatility input must not be empty")

    frame = data.loc[:, ["timestamp_utc", "close"]].copy()
    frame["timestamp_utc"] = pd.to_datetime(frame["timestamp_utc"], utc=True, errors="coerce")
    frame["close"] = pd.to_numeric(frame["close"], errors="coerce")
    frame = frame.sort_values("timestamp_utc").reset_index(drop=True)

    if frame["timestamp_utc"].isna().any():
        raise ValueError("historical volatility input contains invalid timestamps")
    if frame["timestamp_utc"].duplicated().any():
        raise ValueError("historical volatility input contains duplicate timestamps")
    if frame["close"].isna().any():
        raise ValueError("historical volatility input close column contains missing values")
    if (frame["close"] <= 0).any():
        raise ValueError("historical volatility input close column must be positive")
    if len(frame) < window + 1:
        raise ValueError("historical volatility input does not contain enough rows for window")
    return frame
