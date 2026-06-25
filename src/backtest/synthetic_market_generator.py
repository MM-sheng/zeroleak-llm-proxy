"""Synthetic BTC market generation for backtests."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

import pandas as pd


@dataclass(frozen=True)
class SyntheticBTCMarket:
    """Synthetic BTC market definition for offline backtests."""

    market_id: str
    question: str
    event_type: str
    direction: str
    target_price: float
    decision_time_utc: datetime
    deadline_utc: datetime
    initial_price: float


def generate_synthetic_btc_markets(
    price_data: pd.DataFrame,
    *,
    target_multipliers: tuple[float, ...] = (1.05, 1.10, 0.95),
    days_to_expiry: int = 7,
    event_type: str = "touch",
) -> list[SyntheticBTCMarket]:
    """Generate synthetic BTC target markets from historical price rows."""
    if days_to_expiry <= 0:
        raise ValueError("days_to_expiry must be positive")
    if event_type not in {"touch", "terminal"}:
        raise ValueError("event_type must be touch or terminal")
    if not target_multipliers:
        raise ValueError("at least one target multiplier is required")

    frame = _validate_price_data(price_data)
    markets: list[SyntheticBTCMarket] = []
    for row_index, row in frame.iterrows():
        decision_time = row["timestamp_utc"].to_pydatetime()
        initial_price = float(row["close"])
        deadline = decision_time + pd.Timedelta(days=days_to_expiry)
        for multiplier in target_multipliers:
            if multiplier <= 0:
                raise ValueError("target multipliers must be positive")
            target_price = round(initial_price * float(multiplier), 2)
            direction = "above" if multiplier >= 1.0 else "below"
            market_id = f"synthetic-btc-{event_type}-{row_index}-{multiplier:.4f}"
            verb = "touch" if event_type == "touch" else "close"
            relation = "above" if direction == "above" else "below"
            question = (
                f"Will BTC {verb} {relation} ${target_price:,.2f} "
                f"by {deadline.date().isoformat()}?"
            )
            markets.append(
                SyntheticBTCMarket(
                    market_id=market_id,
                    question=question,
                    event_type=event_type,
                    direction=direction,
                    target_price=target_price,
                    decision_time_utc=decision_time,
                    deadline_utc=deadline,
                    initial_price=initial_price,
                )
            )
    return markets


def generate_weekly_touch_markets(price_data: pd.DataFrame) -> list[SyntheticBTCMarket]:
    """Generate standard weekly synthetic BTC touch markets."""
    return generate_synthetic_btc_markets(
        price_data,
        target_multipliers=(1.05, 1.10, 0.95),
        days_to_expiry=7,
        event_type="touch",
    )


def _validate_price_data(price_data: pd.DataFrame) -> pd.DataFrame:
    """Validate minimal canonical price data for synthetic market generation."""
    if not isinstance(price_data, pd.DataFrame):
        raise TypeError("price_data must be a pandas DataFrame")
    missing = [column for column in ["timestamp_utc", "close"] if column not in price_data.columns]
    if missing:
        raise ValueError(f"price_data missing required columns: {missing}")
    if price_data.empty:
        raise ValueError("price_data must not be empty")

    frame = price_data.loc[:, ["timestamp_utc", "close"]].copy()
    frame["timestamp_utc"] = pd.to_datetime(frame["timestamp_utc"], utc=True, errors="coerce")
    frame["close"] = pd.to_numeric(frame["close"], errors="coerce")
    frame = frame.sort_values("timestamp_utc").reset_index(drop=True)
    if frame["timestamp_utc"].isna().any():
        raise ValueError("price_data contains invalid timestamps")
    if frame["close"].isna().any() or (frame["close"] <= 0).any():
        raise ValueError("price_data close values must be positive")
    return frame
