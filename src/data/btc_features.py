"""BTC feature engineering utilities for canonical OHLCV data."""

from __future__ import annotations

import numpy as np
import pandas as pd


def add_returns(data: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with one-period simple and log close-to-close returns.

    The function assumes canonical OHLCV input from ``BTCPriceLoader`` and does
    not use future rows. The first row has missing returns because no prior
    close is available.
    """
    _validate_return_input(data)
    result = data.copy()
    result["return_1_period"] = result["close"].pct_change()
    result["log_return_1_period"] = np.log(result["close"] / result["close"].shift(1))
    return result


def add_realized_volatility(
    data: pd.DataFrame,
    *,
    window: int,
    periods_per_year: int,
    output_column: str | None = None,
) -> pd.DataFrame:
    """Return a copy with annualized rolling realized volatility.

    Volatility is computed from past close-to-close log returns only. The
    current row's value uses the current and previous rows' returns inside the
    rolling window, never future rows.
    """
    _validate_volatility_input(window=window, periods_per_year=periods_per_year)
    result = data.copy()
    if "log_return_1_period" not in result.columns:
        result = add_returns(result)

    column = output_column or f"realized_volatility_{window}_period"
    result[column] = (
        result["log_return_1_period"].rolling(window=window, min_periods=window).std()
        * np.sqrt(periods_per_year)
    )
    return result


def add_distance_to_target_price(data: pd.DataFrame, *, target_price: float) -> pd.DataFrame:
    """Return a copy with close-price distance to a USD target price.

    The USD distance is ``target_price - close``. Positive values mean the
    target is above the current close; negative values mean it is below. The
    percentage distance is measured relative to the current close.
    """
    _validate_target_input(data=data, target_price=target_price)
    result = data.copy()
    target = float(target_price)
    result["target_price_usd"] = target
    result["distance_to_target_price_usd"] = target - result["close"]
    result["distance_to_target_price_pct"] = result["distance_to_target_price_usd"] / result["close"]
    return result


def _validate_return_input(data: pd.DataFrame) -> None:
    """Validate the minimal columns required for close-to-close returns."""
    if not isinstance(data, pd.DataFrame):
        raise TypeError("returns input must be a pandas DataFrame")
    missing = [column for column in ["timestamp_utc", "close"] if column not in data.columns]
    if missing:
        raise ValueError(f"returns input missing required columns: {missing}")
    if data.empty:
        raise ValueError("returns input must not be empty")
    if data["close"].isna().any():
        raise ValueError("returns input close column contains missing values")
    if (data["close"] <= 0).any():
        raise ValueError("returns input close column must be positive")


def _validate_volatility_input(*, window: int, periods_per_year: int) -> None:
    """Validate realized-volatility window and annualization settings."""
    if window < 2:
        raise ValueError("realized volatility window must be at least 2")
    if periods_per_year <= 0:
        raise ValueError("periods_per_year must be positive")


def _validate_target_input(*, data: pd.DataFrame, target_price: float) -> None:
    """Validate the minimal inputs required for target-distance features."""
    if not isinstance(data, pd.DataFrame):
        raise TypeError("target distance input must be a pandas DataFrame")
    missing = [column for column in ["timestamp_utc", "close"] if column not in data.columns]
    if missing:
        raise ValueError(f"target distance input missing required columns: {missing}")
    if data.empty:
        raise ValueError("target distance input must not be empty")
    if pd.isna(target_price) or float(target_price) <= 0:
        raise ValueError("target_price must be positive")
    if data["close"].isna().any():
        raise ValueError("target distance input close column contains missing values")
    if (data["close"] <= 0).any():
        raise ValueError("target distance input close column must be positive")
