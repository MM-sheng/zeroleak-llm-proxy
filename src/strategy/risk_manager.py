"""Paper-trading risk controls."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class RiskDecision:
    """Risk approval result for a proposed paper position."""

    allowed: bool
    approved_size_usd: float
    max_loss_usd: float
    reasons: tuple[str, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)


def apply_risk_limits(
    *,
    bankroll_usd: float,
    proposed_size_usd: float,
    current_btc_exposure_usd: float = 0.0,
    daily_pnl_usd: float = 0.0,
    weekly_pnl_usd: float = 0.0,
    liquidity_usd: float | None = None,
    min_liquidity_usd: float = 0.0,
    spread: float | None = None,
    max_spread: float | None = None,
    rules_clear: bool = True,
    max_single_trade_fraction: float = 0.01,
    max_btc_exposure_fraction: float = 0.10,
    daily_loss_limit_fraction: float = 0.03,
    weekly_loss_limit_fraction: float = 0.08,
) -> RiskDecision:
    """Apply paper-only risk limits to a proposed position size."""
    bankroll = _positive("bankroll_usd", bankroll_usd)
    proposed = _non_negative("proposed_size_usd", proposed_size_usd)
    exposure = _non_negative("current_btc_exposure_usd", current_btc_exposure_usd)
    _non_negative("min_liquidity_usd", min_liquidity_usd)
    _fraction("max_single_trade_fraction", max_single_trade_fraction)
    _fraction("max_btc_exposure_fraction", max_btc_exposure_fraction)
    _fraction("daily_loss_limit_fraction", daily_loss_limit_fraction)
    _fraction("weekly_loss_limit_fraction", weekly_loss_limit_fraction)

    reasons: list[str] = []
    warnings: list[str] = []
    if not rules_clear:
        reasons.append("rules_unclear")
    if daily_pnl_usd <= -(bankroll * daily_loss_limit_fraction):
        reasons.append("daily_loss_limit_reached")
    if weekly_pnl_usd <= -(bankroll * weekly_loss_limit_fraction):
        reasons.append("weekly_loss_limit_reached")
    if liquidity_usd is not None and liquidity_usd < min_liquidity_usd:
        reasons.append("low_liquidity")
    if spread is not None and max_spread is not None and spread > max_spread:
        reasons.append("wide_spread")
    if reasons:
        return RiskDecision(False, 0.0, 0.0, reasons=tuple(reasons), warnings=tuple(warnings))

    single_trade_cap = bankroll * max_single_trade_fraction
    aggregate_cap_remaining = max(0.0, bankroll * max_btc_exposure_fraction - exposure)
    approved = min(proposed, single_trade_cap, aggregate_cap_remaining)
    if approved < proposed:
        warnings.append("position_size_reduced_by_risk_limits")
    if approved <= 0:
        return RiskDecision(False, 0.0, 0.0, reasons=("btc_exposure_limit_reached",), warnings=tuple(warnings))

    return RiskDecision(True, approved, approved, reasons=(), warnings=tuple(warnings))


def _positive(name: str, value: float) -> float:
    """Validate positive numeric input."""
    number = float(value)
    if number <= 0:
        raise ValueError(f"{name} must be positive")
    return number


def _non_negative(name: str, value: float) -> float:
    """Validate non-negative numeric input."""
    number = float(value)
    if number < 0:
        raise ValueError(f"{name} must be non-negative")
    return number


def _fraction(name: str, value: float) -> float:
    """Validate a non-negative risk fraction."""
    number = float(value)
    if number < 0:
        raise ValueError(f"{name} must be non-negative")
    return number
