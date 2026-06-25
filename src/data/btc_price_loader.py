"""BTC historical price loading.

The default data source is Yahoo Finance via ``yfinance`` and the default
symbol is ``BTC-USD``. Tests can inject a downloader so they stay offline.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import pandas as pd

REQUIRED_SCHEMA = ["timestamp_utc", "open", "high", "low", "close", "volume"]


class BTCPriceLoadError(RuntimeError):
    """Raised when BTC price data cannot be loaded."""


Downloader = Callable[..., pd.DataFrame]


@dataclass(frozen=True)
class BTCPriceLoader:
    """Load BTC OHLCV history from a configured market data source."""

    symbol: str = "BTC-USD"
    timeout_seconds: int = 30
    downloader: Downloader | None = None

    def __post_init__(self) -> None:
        """Validate loader configuration."""
        if not self.symbol or not self.symbol.strip():
            raise ValueError("symbol must be a non-empty string")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")

    def load_history(
        self,
        *,
        period: str = "1y",
        interval: str = "1d",
        auto_adjust: bool = False,
    ) -> pd.DataFrame:
        """Return BTC historical prices using the canonical project schema."""
        data = self._download(
            tickers=self.symbol,
            period=period,
            interval=interval,
            auto_adjust=auto_adjust,
            progress=False,
            timeout=self.timeout_seconds,
        )
        return self.standardize_schema(data, expected_interval=interval)

    @classmethod
    def standardize_schema(
        cls,
        data: pd.DataFrame,
        *,
        expected_interval: str | None = None,
    ) -> pd.DataFrame:
        """Normalize price data to timestamped UTC OHLCV columns.

        The returned DataFrame columns are exactly ``timestamp_utc``, ``open``,
        ``high``, ``low``, ``close``, and ``volume``. Invalid, duplicate, or
        incomplete source data raises ``BTCPriceLoadError``.
        """
        frame = cls._ensure_non_empty_frame(data)
        frame = cls._flatten_yfinance_columns(frame)
        frame = frame.rename(columns=cls._normalized_column_map(frame))
        frame = cls._add_timestamp_column(frame)

        missing = [column for column in REQUIRED_SCHEMA if column not in frame.columns]
        if missing:
            raise BTCPriceLoadError(f"price data missing required columns: {missing}")

        result = frame.loc[:, REQUIRED_SCHEMA].copy()
        result["timestamp_utc"] = pd.to_datetime(result["timestamp_utc"], utc=True, errors="coerce")
        result = result.sort_values("timestamp_utc").reset_index(drop=True)

        if result["timestamp_utc"].duplicated().any():
            raise BTCPriceLoadError("price data contains duplicate UTC timestamps")
        if result["timestamp_utc"].isna().any():
            raise BTCPriceLoadError("price data contains invalid UTC timestamps")
        cls._validate_expected_interval(result, expected_interval=expected_interval)

        numeric_columns = ["open", "high", "low", "close", "volume"]
        for column in numeric_columns:
            result[column] = pd.to_numeric(result[column], errors="coerce")
        if result[numeric_columns].isna().any().any():
            raise BTCPriceLoadError("price data contains missing or non-numeric OHLCV values")

        price_columns = ["open", "high", "low", "close"]
        if (result[price_columns] <= 0).any().any():
            raise BTCPriceLoadError("price data contains non-positive OHLC prices")
        if (result["volume"] < 0).any():
            raise BTCPriceLoadError("price data contains negative volume")
        if (result["high"] < result[["open", "low", "close"]].max(axis=1)).any():
            raise BTCPriceLoadError("price data contains high below open, low, or close")
        if (result["low"] > result[["open", "high", "close"]].min(axis=1)).any():
            raise BTCPriceLoadError("price data contains low above open, high, or close")

        return result

    def _download(self, **kwargs: Any) -> pd.DataFrame:
        """Call the injected downloader or lazily import ``yfinance``."""
        if self.downloader is not None:
            return self.downloader(**kwargs)

        try:
            import yfinance as yf
        except ModuleNotFoundError as exc:
            raise BTCPriceLoadError(
                "yfinance is required for live BTC price loading; install requirements.txt"
            ) from exc

        return yf.download(**kwargs)

    @staticmethod
    def _ensure_non_empty_frame(data: pd.DataFrame) -> pd.DataFrame:
        """Validate that the data source returned a non-empty DataFrame."""
        if not isinstance(data, pd.DataFrame):
            raise BTCPriceLoadError("price downloader must return a pandas DataFrame")
        if data.empty:
            raise BTCPriceLoadError("price downloader returned no BTC price rows")
        return data.copy()

    @staticmethod
    def _flatten_yfinance_columns(data: pd.DataFrame) -> pd.DataFrame:
        """Flatten common yfinance MultiIndex columns to field names."""
        if not isinstance(data.columns, pd.MultiIndex):
            return data

        flattened = data.copy()
        flattened.columns = [
            next(
                (part for part in column if str(part).lower() in {"open", "high", "low", "close", "volume"}),
                column[-1],
            )
            for column in flattened.columns
        ]
        return flattened

    @staticmethod
    def _normalized_column_map(data: pd.DataFrame) -> dict[str, str]:
        """Return a rename map from source OHLCV names to canonical names."""
        aliases = {
            "date": "timestamp_utc",
            "datetime": "timestamp_utc",
            "timestamp": "timestamp_utc",
            "timestamp_utc": "timestamp_utc",
            "open": "open",
            "high": "high",
            "low": "low",
            "close": "close",
            "volume": "volume",
        }
        rename_map = {}
        for column in data.columns:
            normalized = str(column).strip().lower().replace(" ", "_")
            if normalized in aliases:
                rename_map[column] = aliases[normalized]
        return rename_map

    @staticmethod
    def _add_timestamp_column(data: pd.DataFrame) -> pd.DataFrame:
        """Use an existing timestamp column or the DataFrame index as UTC time."""
        frame = data.copy()
        if "timestamp_utc" not in frame.columns:
            frame["timestamp_utc"] = frame.index
        return frame

    @staticmethod
    def _validate_expected_interval(
        data: pd.DataFrame,
        *,
        expected_interval: str | None,
    ) -> None:
        """Raise when consecutive timestamps skip the requested fixed interval."""
        if expected_interval is None or len(data) < 2:
            return

        interval = expected_interval.strip().lower()
        expected_delta = {
            "1m": pd.Timedelta(minutes=1),
            "2m": pd.Timedelta(minutes=2),
            "5m": pd.Timedelta(minutes=5),
            "15m": pd.Timedelta(minutes=15),
            "30m": pd.Timedelta(minutes=30),
            "60m": pd.Timedelta(minutes=60),
            "90m": pd.Timedelta(minutes=90),
            "1h": pd.Timedelta(hours=1),
            "1d": pd.Timedelta(days=1),
            "5d": pd.Timedelta(days=5),
            "1wk": pd.Timedelta(weeks=1),
        }.get(interval)
        if expected_delta is None:
            return

        gaps = data["timestamp_utc"].diff().dropna()
        if (gaps > expected_delta).any():
            raise BTCPriceLoadError(
                f"price data contains timestamp gaps larger than expected interval {expected_interval}"
            )
