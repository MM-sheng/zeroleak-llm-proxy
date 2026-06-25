"""Markdown daily report generation for paper-trading research."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping


@dataclass(frozen=True)
class DailyReportMarket:
    """One market row in the daily report."""

    market_id: str
    question: str
    yes_price: float | None
    no_price: float | None
    model_probability: float | None
    edge: float | None
    action: str
    suggested_limit_price: float | None
    suggested_position_usd: float
    reasons_not_to_trade: tuple[str, ...] = field(default_factory=tuple)
    model_uncertainty: str = "unknown"


@dataclass(frozen=True)
class DailyReport:
    """Input model for a BTC Polymarket paper-trading daily report."""

    generated_at_utc: datetime
    btc_current_state: Mapping[str, object]
    markets: tuple[DailyReportMarket, ...] = field(default_factory=tuple)
    best_opportunity: str = "No paper opportunity selected."
    largest_risk: str = "Model uncertainty and market liquidity may invalidate any signal."
    model_uncertainty: str = "Model outputs are estimates, not true probabilities."


def render_daily_report(report: DailyReport) -> str:
    """Render a daily paper-trading report as Markdown."""
    generated_at = _normalize_timestamp(report.generated_at_utc)
    lines = [
        "# BTC Polymarket Daily Paper Report",
        "",
        f"- Generated at UTC: {generated_at.isoformat()}",
        "- Mode: paper-only research; no real orders, wallet, or live trading.",
        "",
        "## BTC Current State",
        *_render_mapping(report.btc_current_state),
        "",
        "## BTC Polymarket Markets Scanned Today",
        *_render_market_table(report.markets),
        "",
        "## YES Price And NO Price Per Market",
        *_render_price_lines(report.markets),
        "",
        "## Model Probability",
        *_render_probability_lines(report.markets),
        "",
        "## Edge",
        *_render_edge_lines(report.markets),
        "",
        "## Action",
        *_render_action_lines(report.markets),
        "",
        "## Suggested Limit Price",
        *_render_limit_lines(report.markets),
        "",
        "## Suggested Position",
        *_render_position_lines(report.markets),
        "",
        "## Reasons Not To Trade",
        *_render_reasons_lines(report.markets),
        "",
        "## Best Opportunity To Watch",
        f"- {report.best_opportunity}",
        "",
        "## Largest Risk",
        f"- {report.largest_risk}",
        "",
        "## Model Uncertainty",
        f"- {report.model_uncertainty}",
        "",
    ]
    return "\n".join(lines)


def write_daily_report(path: str | Path, report: DailyReport) -> str:
    """Write a Markdown daily report and return the rendered content."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    content = render_daily_report(report)
    output_path.write_text(content, encoding="utf-8")
    return content


def _normalize_timestamp(timestamp: datetime) -> datetime:
    """Return a timezone-aware UTC timestamp."""
    if timestamp.tzinfo is None:
        raise ValueError("generated_at_utc must be timezone-aware")
    return timestamp.astimezone(timezone.utc)


def _render_mapping(values: Mapping[str, object]) -> list[str]:
    """Render a simple key-value mapping."""
    if not values:
        return ["- No BTC state supplied."]
    return [f"- {key}: {value}" for key, value in values.items()]


def _render_market_table(markets: tuple[DailyReportMarket, ...]) -> list[str]:
    """Render the market scan table."""
    if not markets:
        return ["- No BTC markets scanned."]
    lines = ["| Market ID | Question | YES | NO | Action |", "| --- | --- | ---: | ---: | --- |"]
    for market in markets:
        lines.append(
            f"| {market.market_id} | {market.question} | {_fmt_probability(market.yes_price)} | "
            f"{_fmt_probability(market.no_price)} | {market.action} |"
        )
    return lines


def _render_price_lines(markets: tuple[DailyReportMarket, ...]) -> list[str]:
    """Render YES/NO prices."""
    return _market_lines(
        markets,
        lambda market: f"{market.market_id}: YES {_fmt_probability(market.yes_price)}, NO {_fmt_probability(market.no_price)}",
    )


def _render_probability_lines(markets: tuple[DailyReportMarket, ...]) -> list[str]:
    """Render model probabilities."""
    return _market_lines(markets, lambda market: f"{market.market_id}: {_fmt_probability(market.model_probability)}")


def _render_edge_lines(markets: tuple[DailyReportMarket, ...]) -> list[str]:
    """Render edge values."""
    return _market_lines(markets, lambda market: f"{market.market_id}: {_fmt_signed(market.edge)}")


def _render_action_lines(markets: tuple[DailyReportMarket, ...]) -> list[str]:
    """Render actions."""
    return _market_lines(markets, lambda market: f"{market.market_id}: {market.action}")


def _render_limit_lines(markets: tuple[DailyReportMarket, ...]) -> list[str]:
    """Render suggested limit prices."""
    return _market_lines(
        markets,
        lambda market: f"{market.market_id}: {_fmt_probability(market.suggested_limit_price)}",
    )


def _render_position_lines(markets: tuple[DailyReportMarket, ...]) -> list[str]:
    """Render paper position sizes."""
    return _market_lines(markets, lambda market: f"{market.market_id}: {_fmt_usd(market.suggested_position_usd)}")


def _render_reasons_lines(markets: tuple[DailyReportMarket, ...]) -> list[str]:
    """Render reasons not to trade."""
    return _market_lines(
        markets,
        lambda market: f"{market.market_id}: {', '.join(market.reasons_not_to_trade) or 'No blocking reason recorded.'}",
    )


def _market_lines(markets: tuple[DailyReportMarket, ...], formatter: object) -> list[str]:
    """Render one bullet per market."""
    if not markets:
        return ["- No market data supplied."]
    return [f"- {formatter(market)}" for market in markets]


def _fmt_probability(value: float | None) -> str:
    """Format a probability-like price."""
    if value is None:
        return "n/a"
    return f"{float(value):.2%}"


def _fmt_signed(value: float | None) -> str:
    """Format a signed edge value."""
    if value is None:
        return "n/a"
    return f"{float(value):+.2%}"


def _fmt_usd(value: float) -> str:
    """Format a USD paper position."""
    return f"${float(value):,.2f} USD"
