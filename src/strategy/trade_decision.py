"""Paper-only trade decision assembly."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from src.strategy.edge_calculator import calculate_edges
from src.strategy.expected_value import calculate_expected_value
from src.strategy.kelly_sizing import calculate_kelly_sizing
from src.strategy.risk_manager import apply_risk_limits


TradeAction = Literal["BUY_YES", "BUY_NO", "HOLD"]


@dataclass(frozen=True)
class TradeDecision:
    """Paper-only trade decision output."""

    action: TradeAction
    model_probability: float
    market_price: float | None
    edge: float
    expected_value: float
    suggested_limit_price: float | None
    position_size_usd: float
    max_loss_usd: float
    confidence: float
    reasons: tuple[str, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)


def make_trade_decision(
    *,
    model_probability: float,
    yes_price: float,
    no_price: float,
    bankroll_usd: float,
    confidence: float = 1.0,
    min_edge: float = 0.0,
    min_expected_value: float = 0.0,
    calibration_is_poor: bool = False,
    **risk_kwargs: float | bool | None,
) -> TradeDecision:
    """Build a paper-only BUY_YES, BUY_NO, or HOLD decision."""
    if not 0.0 <= float(confidence) <= 1.0:
        raise ValueError("confidence must be between 0 and 1")
    edges = calculate_edges(model_probability=model_probability, yes_price=yes_price, no_price=no_price)
    expected_value = calculate_expected_value(model_probability=model_probability, yes_price=yes_price, no_price=no_price)

    reasons: list[str] = []
    warnings = [*edges.warnings, *expected_value.warnings]
    if edges.best_side == "NONE" or edges.best_edge <= min_edge:
        reasons.append("edge_below_threshold")
    if expected_value.best_side == "NONE" or expected_value.best_ev <= min_expected_value:
        reasons.append("expected_value_below_threshold")
    if edges.best_side != expected_value.best_side:
        reasons.append("edge_ev_side_disagreement")

    if reasons:
        return _hold(
            model_probability=edges.model_probability,
            confidence=float(confidence),
            reasons=tuple(reasons),
            warnings=tuple(warnings),
        )

    if calibration_is_poor:
        warnings.append("calibration_blocked_buy_signal")
        return _hold(
            model_probability=edges.model_probability,
            confidence=float(confidence),
            reasons=("poor_calibration",),
            warnings=tuple(warnings),
        )

    selected_price = yes_price if expected_value.best_side == "YES" else no_price
    selected_probability = model_probability if expected_value.best_side == "YES" else 1.0 - model_probability
    sizing = calculate_kelly_sizing(
        probability=selected_probability,
        price=selected_price,
        bankroll_usd=bankroll_usd,
    )
    warnings.extend(sizing.warnings)
    risk = apply_risk_limits(
        bankroll_usd=bankroll_usd,
        proposed_size_usd=sizing.position_size_usd,
        **risk_kwargs,
    )
    warnings.extend(risk.warnings)
    if not risk.allowed:
        return _hold(
            model_probability=edges.model_probability,
            confidence=float(confidence),
            reasons=tuple(risk.reasons),
            warnings=tuple(warnings),
        )

    action: TradeAction = "BUY_YES" if expected_value.best_side == "YES" else "BUY_NO"
    return TradeDecision(
        action=action,
        model_probability=edges.model_probability,
        market_price=float(selected_price),
        edge=edges.edge_yes if action == "BUY_YES" else edges.edge_no,
        expected_value=expected_value.ev_yes if action == "BUY_YES" else expected_value.ev_no,
        suggested_limit_price=float(selected_price),
        position_size_usd=risk.approved_size_usd,
        max_loss_usd=risk.max_loss_usd,
        confidence=float(confidence),
        reasons=("paper_only_decision",),
        warnings=tuple(warnings),
    )


def _hold(
    *,
    model_probability: float,
    confidence: float,
    reasons: tuple[str, ...],
    warnings: tuple[str, ...],
) -> TradeDecision:
    """Return a HOLD decision."""
    return TradeDecision(
        action="HOLD",
        model_probability=float(model_probability),
        market_price=None,
        edge=0.0,
        expected_value=0.0,
        suggested_limit_price=None,
        position_size_usd=0.0,
        max_loss_usd=0.0,
        confidence=confidence,
        reasons=reasons,
        warnings=warnings,
    )
