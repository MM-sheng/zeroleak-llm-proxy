"""Mark-to-market helpers for paper-only positions."""

from __future__ import annotations

from dataclasses import replace
from typing import Mapping

from src.paper.paper_executor import PaperExecution


def mark_paper_execution(execution: PaperExecution, *, current_price: float) -> PaperExecution:
    """Return an updated paper execution with unrealized PnL at current price."""
    price = _probability("current_price", current_price)
    if execution.status != "OPEN" or execution.side == "NONE":
        return replace(execution, current_price=price, mark_to_market_pnl=0.0)
    if execution.entry_price is None:
        raise ValueError("open paper executions require an entry_price")
    entry_price = _probability("entry_price", execution.entry_price)
    if entry_price <= 0.0:
        raise ValueError("entry_price must be greater than zero for mark-to-market")
    shares = execution.size_usd / entry_price
    pnl = shares * price - execution.size_usd
    return replace(execution, current_price=price, mark_to_market_pnl=pnl)


def mark_journal_row(row: Mapping[str, object], *, current_price: float) -> dict[str, object]:
    """Return an updated journal row with current price and mark-to-market PnL."""
    price = _probability("current_price", current_price)
    updated = dict(row)
    if updated.get("side") == "NONE" or updated.get("action") == "HOLD":
        updated["current_price"] = price
        updated["mark_to_market_pnl"] = 0.0
        return updated

    entry_price = _probability("entry_price", updated.get("entry_price"))
    if entry_price <= 0.0:
        raise ValueError("entry_price must be greater than zero for mark-to-market")
    size_usd = float(updated.get("size_usd", 0.0))
    if size_usd < 0.0:
        raise ValueError("size_usd must be non-negative")
    shares = size_usd / entry_price
    updated["current_price"] = price
    updated["mark_to_market_pnl"] = shares * price - size_usd
    return updated


def _probability(name: str, value: object) -> float:
    """Validate and return a probability-like price."""
    if value is None:
        raise ValueError(f"{name} is required")
    number = float(value)
    if not 0.0 <= number <= 1.0:
        raise ValueError(f"{name} must be between 0 and 1")
    return number
