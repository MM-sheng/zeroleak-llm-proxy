"""Manual resolution helpers for paper-only trades."""

from __future__ import annotations

from dataclasses import replace
from typing import Literal, Mapping

from src.paper.paper_executor import PaperExecution


ManualResolution = Literal["YES", "NO", "VOID"]


def resolve_paper_execution(
    execution: PaperExecution,
    *,
    final_resolution: ManualResolution,
    lesson: str = "",
) -> PaperExecution:
    """Return a paper execution with manually entered final resolution and PnL."""
    resolution = _normalize_resolution(final_resolution)
    realized_pnl = _calculate_realized_pnl(
        side=execution.side,
        entry_price=execution.entry_price,
        size_usd=execution.size_usd,
        final_resolution=resolution,
    )
    return replace(
        execution,
        final_resolution=resolution,
        realized_pnl=realized_pnl,
        current_price=_terminal_price(execution.side, resolution),
        mark_to_market_pnl=realized_pnl,
        lesson=str(lesson),
    )


def resolve_journal_row(
    row: Mapping[str, object],
    *,
    final_resolution: ManualResolution,
    lesson: str = "",
) -> dict[str, object]:
    """Return a journal row updated with manual final resolution and realized PnL."""
    resolution = _normalize_resolution(final_resolution)
    updated = dict(row)
    side = str(updated.get("side", "NONE"))
    realized_pnl = _calculate_realized_pnl(
        side=side,
        entry_price=updated.get("entry_price"),
        size_usd=float(updated.get("size_usd", 0.0)),
        final_resolution=resolution,
    )
    updated["final_resolution"] = resolution
    updated["realized_pnl"] = realized_pnl
    updated["current_price"] = _terminal_price(side, resolution)
    updated["mark_to_market_pnl"] = realized_pnl
    updated["lesson"] = str(lesson)
    return updated


def _calculate_realized_pnl(
    *,
    side: str,
    entry_price: object,
    size_usd: float,
    final_resolution: ManualResolution,
) -> float:
    """Calculate binary contract realized PnL for a manual paper resolution."""
    if side == "NONE" or final_resolution == "VOID":
        return 0.0
    if side not in {"YES", "NO"}:
        raise ValueError("side must be YES, NO, or NONE")
    if size_usd < 0.0:
        raise ValueError("size_usd must be non-negative")
    entry = _entry_price(entry_price)
    shares = size_usd / entry
    winning_side = "YES" if final_resolution == "YES" else "NO"
    payout = shares if side == winning_side else 0.0
    return payout - size_usd


def _terminal_price(side: str, final_resolution: ManualResolution) -> float | None:
    """Return the terminal price for the held side after resolution."""
    if side == "NONE" or final_resolution == "VOID":
        return None
    return 1.0 if side == final_resolution else 0.0


def _normalize_resolution(final_resolution: str) -> ManualResolution:
    """Normalize and validate manual resolution input."""
    resolution = str(final_resolution).strip().upper()
    if resolution not in {"YES", "NO", "VOID"}:
        raise ValueError("final_resolution must be YES, NO, or VOID")
    return resolution  # type: ignore[return-value]


def _entry_price(value: object) -> float:
    """Validate an entry price used for realized PnL."""
    if value is None:
        raise ValueError("entry_price is required for resolved positions")
    number = float(value)
    if not 0.0 < number <= 1.0:
        raise ValueError("entry_price must be greater than 0 and at most 1")
    return number
