"""Kelly sizing utilities for paper-only position sizing."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class KellySizingResult:
    """Kelly sizing output before portfolio risk controls."""

    probability: float
    price: float
    bankroll_usd: float
    base_kelly_fraction: float
    quarter_kelly_fraction: float
    position_size_usd: float
    max_loss_usd: float
    warnings: tuple[str, ...] = field(default_factory=tuple)


def calculate_kelly_sizing(
    *,
    probability: float,
    price: float,
    bankroll_usd: float,
) -> KellySizingResult:
    """Calculate quarter-Kelly paper sizing for a binary market price."""
    p = _validate_probability("probability", probability)
    market_price = _validate_price(price)
    bankroll = float(bankroll_usd)
    if bankroll <= 0:
        raise ValueError("bankroll_usd must be positive")

    raw_kelly = (p - market_price) / (1.0 - market_price)
    warnings: list[str] = []
    base_kelly = max(0.0, raw_kelly)
    if raw_kelly <= 0:
        warnings.append("non_positive_kelly")
    quarter_kelly = base_kelly / 4.0
    position_size = bankroll * quarter_kelly

    return KellySizingResult(
        probability=p,
        price=market_price,
        bankroll_usd=bankroll,
        base_kelly_fraction=base_kelly,
        quarter_kelly_fraction=quarter_kelly,
        position_size_usd=position_size,
        max_loss_usd=position_size,
        warnings=tuple(warnings),
    )


def _validate_probability(name: str, value: float) -> float:
    """Validate a probability-like input."""
    probability = float(value)
    if not 0.0 <= probability <= 1.0:
        raise ValueError(f"{name} must be between 0 and 1")
    return probability


def _validate_price(value: float) -> float:
    """Validate a binary market entry price."""
    price = float(value)
    if not 0.0 <= price < 1.0:
        raise ValueError("price must be between 0 inclusive and 1 exclusive")
    return price
