"""Bootstrap fat-tail probability model."""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil
from typing import Iterable, Literal

import numpy as np


BootstrapMode = Literal["touch", "terminal"]


@dataclass(frozen=True)
class BootstrapFatTailResult:
    """Bootstrap probability estimate from historical BTC log returns."""

    probability: float
    terminal_probability: float
    touch_probability: float
    expected_max_price: float
    expected_min_price: float
    quantiles: dict[str, float]
    diagnostics: dict[str, float | int | str | None]


def run_bootstrap_fat_tail_model(
    *,
    current_price: float,
    target_price: float,
    historical_log_returns: Iterable[float],
    days_to_expiry: float,
    n_paths: int = 10_000,
    random_seed: int | None = None,
    mode: BootstrapMode = "terminal",
) -> BootstrapFatTailResult:
    """Estimate target probabilities by resampling historical log returns."""
    returns = _coerce_returns(historical_log_returns)
    _validate_inputs(
        current_price=current_price,
        target_price=target_price,
        returns=returns,
        days_to_expiry=days_to_expiry,
        n_paths=n_paths,
        mode=mode,
    )

    steps = max(1, ceil(days_to_expiry))
    rng = np.random.default_rng(random_seed)
    sampled_returns = rng.choice(returns, size=(n_paths, steps), replace=True)
    simulated_paths = current_price * np.exp(np.cumsum(sampled_returns, axis=1))
    paths_with_start = np.concatenate(
        [np.full((n_paths, 1), float(current_price)), simulated_paths],
        axis=1,
    )

    terminal_prices = simulated_paths[:, -1]
    max_prices = paths_with_start.max(axis=1)
    min_prices = paths_with_start.min(axis=1)
    direction = "above" if target_price >= current_price else "below"
    if direction == "above":
        terminal_probability = float(np.mean(terminal_prices >= target_price))
        touch_probability = float(np.mean(max_prices >= target_price))
    else:
        terminal_probability = float(np.mean(terminal_prices <= target_price))
        touch_probability = float(np.mean(min_prices <= target_price))

    probability = terminal_probability if mode == "terminal" else touch_probability
    return BootstrapFatTailResult(
        probability=_clamp_probability(probability),
        terminal_probability=_clamp_probability(terminal_probability),
        touch_probability=_clamp_probability(touch_probability),
        expected_max_price=float(np.mean(max_prices)),
        expected_min_price=float(np.mean(min_prices)),
        quantiles={
            "terminal_p05": float(np.quantile(terminal_prices, 0.05)),
            "terminal_p50": float(np.quantile(terminal_prices, 0.50)),
            "terminal_p95": float(np.quantile(terminal_prices, 0.95)),
        },
        diagnostics={
            "mode": mode,
            "direction": direction,
            "n_paths": n_paths,
            "steps": steps,
            "days_to_expiry": float(days_to_expiry),
            "return_observations": int(len(returns)),
            "random_seed": random_seed,
        },
    )


def _coerce_returns(values: Iterable[float]) -> np.ndarray:
    """Convert historical returns to a clean numeric array."""
    returns = np.array(list(values), dtype=float)
    return returns[np.isfinite(returns)]


def _validate_inputs(
    *,
    current_price: float,
    target_price: float,
    returns: np.ndarray,
    days_to_expiry: float,
    n_paths: int,
    mode: str,
) -> None:
    """Validate bootstrap inputs."""
    if current_price <= 0:
        raise ValueError("current_price must be positive")
    if target_price <= 0:
        raise ValueError("target_price must be positive")
    if len(returns) < 2:
        raise ValueError("historical_log_returns must contain at least two finite values")
    if days_to_expiry <= 0:
        raise ValueError("days_to_expiry must be positive")
    if n_paths <= 0:
        raise ValueError("n_paths must be positive")
    if mode not in {"terminal", "touch"}:
        raise ValueError("mode must be terminal or touch")


def _clamp_probability(value: float) -> float:
    """Clamp floating point probability noise to the valid range."""
    return min(1.0, max(0.0, float(value)))
