"""Paper-only execution records for trade decisions."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal

from src.strategy import TradeDecision


PaperExecutionStatus = Literal["OPEN", "SKIPPED"]
PaperSide = Literal["YES", "NO", "NONE"]


@dataclass(frozen=True)
class PaperExecution:
    """A simulated execution record; it never represents a live order."""

    timestamp_utc: datetime
    market_id: str
    question: str
    action: str
    side: PaperSide
    entry_price: float | None
    model_probability: float
    edge: float
    size_usd: float
    rationale: tuple[str, ...] = field(default_factory=tuple)
    current_price: float | None = None
    mark_to_market_pnl: float = 0.0
    final_resolution: str | None = None
    realized_pnl: float | None = None
    lesson: str = ""
    status: PaperExecutionStatus = "SKIPPED"
    warnings: tuple[str, ...] = field(default_factory=tuple)
    paper_only: bool = True

    def as_journal_row(self) -> dict[str, object]:
        """Return a journal-shaped dictionary without persisting it."""
        return {
            "timestamp_utc": self.timestamp_utc.isoformat(),
            "market_id": self.market_id,
            "question": self.question,
            "action": self.action,
            "side": self.side,
            "entry_price": self.entry_price,
            "model_probability": self.model_probability,
            "edge": self.edge,
            "size_usd": self.size_usd,
            "rationale": list(self.rationale),
            "current_price": self.current_price,
            "mark_to_market_pnl": self.mark_to_market_pnl,
            "final_resolution": self.final_resolution,
            "realized_pnl": self.realized_pnl,
            "lesson": self.lesson,
        }


def execute_paper_decision(
    *,
    decision: TradeDecision,
    market_id: str,
    question: str,
    timestamp_utc: datetime | None = None,
) -> PaperExecution:
    """Convert a trade decision into a paper-only execution record."""
    clean_market_id = str(market_id).strip()
    clean_question = str(question).strip()
    if not clean_market_id:
        raise ValueError("market_id is required")
    if not clean_question:
        raise ValueError("question is required")
    timestamp = _normalize_timestamp(timestamp_utc)

    if decision.action == "HOLD":
        return PaperExecution(
            timestamp_utc=timestamp,
            market_id=clean_market_id,
            question=clean_question,
            action=decision.action,
            side="NONE",
            entry_price=None,
            model_probability=decision.model_probability,
            edge=decision.edge,
            size_usd=0.0,
            rationale=decision.reasons,
            status="SKIPPED",
            warnings=decision.warnings,
        )

    side: PaperSide = "YES" if decision.action == "BUY_YES" else "NO"
    entry_price = _execution_price(decision)
    size_usd = _positive_size(decision.position_size_usd)
    return PaperExecution(
        timestamp_utc=timestamp,
        market_id=clean_market_id,
        question=clean_question,
        action=decision.action,
        side=side,
        entry_price=entry_price,
        model_probability=decision.model_probability,
        edge=decision.edge,
        size_usd=size_usd,
        rationale=decision.reasons,
        current_price=entry_price,
        mark_to_market_pnl=0.0,
        status="OPEN",
        warnings=decision.warnings,
    )


def _normalize_timestamp(timestamp_utc: datetime | None) -> datetime:
    """Return a timezone-aware UTC timestamp."""
    timestamp = timestamp_utc or datetime.now(timezone.utc)
    if timestamp.tzinfo is None:
        raise ValueError("timestamp_utc must be timezone-aware")
    return timestamp.astimezone(timezone.utc)


def _execution_price(decision: TradeDecision) -> float:
    """Resolve and validate the paper entry price from a trade decision."""
    price = decision.suggested_limit_price if decision.suggested_limit_price is not None else decision.market_price
    if price is None:
        raise ValueError("buy decisions require an execution price")
    number = float(price)
    if not 0.0 <= number <= 1.0:
        raise ValueError("execution price must be between 0 and 1")
    return number


def _positive_size(size_usd: float) -> float:
    """Validate a positive USD paper size."""
    number = float(size_usd)
    if number <= 0.0:
        raise ValueError("buy decisions require a positive size_usd")
    return number
