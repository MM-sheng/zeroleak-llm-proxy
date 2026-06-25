"""Probability edge calculation for paper-trading decisions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


EdgeSide = Literal["YES", "NO", "NONE"]


@dataclass(frozen=True)
class EdgeResult:
    """YES/NO edge result against market prices."""

    model_probability: float
    yes_price: float
    no_price: float
    edge_yes: float
    edge_no: float
    best_side: EdgeSide
    best_edge: float
    warnings: tuple[str, ...] = field(default_factory=tuple)


def calculate_edges(
    *,
    model_probability: float,
    yes_price: float,
    no_price: float,
) -> EdgeResult:
    """Calculate YES and NO edge without making a trade recommendation."""
    probability = _validate_probability("model_probability", model_probability)
    yes = _validate_probability("yes_price", yes_price)
    no = _validate_probability("no_price", no_price)
    edge_yes = probability - yes
    edge_no = (1.0 - probability) - no
    warnings: list[str] = []

    if yes + no > 1.05:
        warnings.append("wide_or_inconsistent_prices")
    if edge_yes <= 0 and edge_no <= 0:
        best_side: EdgeSide = "NONE"
        best_edge = max(edge_yes, edge_no)
    elif edge_yes >= edge_no:
        best_side = "YES"
        best_edge = edge_yes
    else:
        best_side = "NO"
        best_edge = edge_no

    return EdgeResult(
        model_probability=probability,
        yes_price=yes,
        no_price=no,
        edge_yes=edge_yes,
        edge_no=edge_no,
        best_side=best_side,
        best_edge=best_edge,
        warnings=tuple(warnings),
    )


def _validate_probability(name: str, value: float) -> float:
    """Validate a probability-like input."""
    probability = float(value)
    if not 0.0 <= probability <= 1.0:
        raise ValueError(f"{name} must be between 0 and 1")
    return probability
