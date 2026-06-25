"""Expected value calculations for YES/NO market prices."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


EVSide = Literal["YES", "NO", "NONE"]


@dataclass(frozen=True)
class ExpectedValueResult:
    """Expected value result per 1 USD of market exposure."""

    model_probability: float
    yes_price: float
    no_price: float
    ev_yes: float
    ev_no: float
    best_side: EVSide
    best_ev: float
    warnings: tuple[str, ...] = field(default_factory=tuple)


def calculate_expected_value(
    *,
    model_probability: float,
    yes_price: float,
    no_price: float,
) -> ExpectedValueResult:
    """Calculate YES and NO expected value without making a trade decision."""
    probability = _validate_probability("model_probability", model_probability)
    yes = _validate_probability("yes_price", yes_price)
    no = _validate_probability("no_price", no_price)
    ev_yes = probability * (1.0 - yes) - (1.0 - probability) * yes
    ev_no = (1.0 - probability) * (1.0 - no) - probability * no
    warnings: list[str] = []

    if yes + no > 1.05:
        warnings.append("wide_or_inconsistent_prices")
    if ev_yes <= 0 and ev_no <= 0:
        best_side: EVSide = "NONE"
        best_ev = max(ev_yes, ev_no)
    elif ev_yes >= ev_no:
        best_side = "YES"
        best_ev = ev_yes
    else:
        best_side = "NO"
        best_ev = ev_no

    return ExpectedValueResult(
        model_probability=probability,
        yes_price=yes,
        no_price=no,
        ev_yes=ev_yes,
        ev_no=ev_no,
        best_side=best_side,
        best_ev=best_ev,
        warnings=tuple(warnings),
    )


def _validate_probability(name: str, value: float) -> float:
    """Validate a probability-like input."""
    probability = float(value)
    if not 0.0 <= probability <= 1.0:
        raise ValueError(f"{name} must be between 0 and 1")
    return probability
