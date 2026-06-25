"""Append-only storage for model predictions and paper recommendations."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping

from src.strategy import TradeDecision


RECOMMENDATION_FIELDS: tuple[str, ...] = (
    "timestamp_utc",
    "market_id",
    "question",
    "model_name",
    "model_probability",
    "model_diagnostics",
    "action",
    "edge",
    "expected_value",
    "suggested_limit_price",
    "position_size_usd",
    "reasons",
    "warnings",
)


@dataclass(frozen=True)
class PredictionRecommendation:
    """Serializable record linking one model prediction to one paper recommendation."""

    timestamp_utc: datetime
    market_id: str
    question: str
    model_name: str
    model_probability: float
    action: str
    edge: float
    expected_value: float
    suggested_limit_price: float | None
    position_size_usd: float
    model_diagnostics: Mapping[str, object] = field(default_factory=dict)
    reasons: tuple[str, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)

    @classmethod
    def from_trade_decision(
        cls,
        *,
        decision: TradeDecision,
        market_id: str,
        question: str,
        model_name: str,
        timestamp_utc: datetime,
        model_diagnostics: Mapping[str, object] | None = None,
    ) -> "PredictionRecommendation":
        """Build a prediction/recommendation record from a paper trade decision."""
        return cls(
            timestamp_utc=timestamp_utc,
            market_id=market_id,
            question=question,
            model_name=model_name,
            model_probability=decision.model_probability,
            model_diagnostics=model_diagnostics or {},
            action=decision.action,
            edge=decision.edge,
            expected_value=decision.expected_value,
            suggested_limit_price=decision.suggested_limit_price,
            position_size_usd=decision.position_size_usd,
            reasons=decision.reasons,
            warnings=decision.warnings,
        )

    def as_dict(self) -> dict[str, object]:
        """Return the canonical JSONL row for this record."""
        row: dict[str, object] = {
            "timestamp_utc": _normalize_timestamp(self.timestamp_utc).isoformat(),
            "market_id": self.market_id,
            "question": self.question,
            "model_name": self.model_name,
            "model_probability": float(self.model_probability),
            "model_diagnostics": dict(self.model_diagnostics),
            "action": self.action,
            "edge": float(self.edge),
            "expected_value": float(self.expected_value),
            "suggested_limit_price": self.suggested_limit_price,
            "position_size_usd": float(self.position_size_usd),
            "reasons": list(self.reasons),
            "warnings": list(self.warnings),
        }
        _validate_row(row)
        return row


@dataclass(frozen=True)
class RecommendationLog:
    """Append-only JSONL store for prediction and recommendation records."""

    path: Path

    def append(self, record: PredictionRecommendation | Mapping[str, object]) -> dict[str, object]:
        """Append one record and return its normalized row."""
        row = normalize_recommendation(record)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
        return row

    def read_all(self) -> list[dict[str, object]]:
        """Read all saved prediction/recommendation rows."""
        if not self.path.exists():
            return []
        rows: list[dict[str, object]] = []
        with self.path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                clean_line = line.strip()
                if not clean_line:
                    continue
                try:
                    payload = json.loads(clean_line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"invalid recommendation JSON on line {line_number}") from exc
                if not isinstance(payload, dict):
                    raise ValueError(f"recommendation row {line_number} must be an object")
                rows.append(normalize_recommendation(payload))
        return rows


def save_prediction_recommendation(
    path: str | Path,
    record: PredictionRecommendation | Mapping[str, object],
) -> dict[str, object]:
    """Save one model prediction and paper recommendation record."""
    return RecommendationLog(Path(path)).append(record)


def read_prediction_recommendations(path: str | Path) -> list[dict[str, object]]:
    """Read saved model prediction and paper recommendation records."""
    return RecommendationLog(Path(path)).read_all()


def normalize_recommendation(record: PredictionRecommendation | Mapping[str, object]) -> dict[str, object]:
    """Normalize a record to the canonical recommendation schema."""
    source = record.as_dict() if isinstance(record, PredictionRecommendation) else dict(record)
    missing = [field for field in RECOMMENDATION_FIELDS if field not in source]
    if missing:
        raise ValueError(f"recommendation missing fields: {', '.join(missing)}")
    normalized = {field: source[field] for field in RECOMMENDATION_FIELDS}
    _validate_row(normalized)
    return normalized


def _normalize_timestamp(timestamp: datetime) -> datetime:
    """Return a timezone-aware UTC timestamp."""
    if timestamp.tzinfo is None:
        raise ValueError("timestamp_utc must be timezone-aware")
    return timestamp.astimezone(timezone.utc)


def _validate_row(row: Mapping[str, object]) -> None:
    """Validate recommendation rows before writing or reading."""
    if not str(row["timestamp_utc"]).strip():
        raise ValueError("timestamp_utc is required")
    for field in ("market_id", "question", "model_name"):
        if not str(row[field]).strip():
            raise ValueError(f"{field} is required")
    _probability("model_probability", row["model_probability"])
    if row["suggested_limit_price"] is not None:
        _probability("suggested_limit_price", row["suggested_limit_price"])
    float(row["edge"])
    float(row["expected_value"])
    if float(row["position_size_usd"]) < 0.0:
        raise ValueError("position_size_usd must be non-negative")
    if row["action"] not in {"BUY_YES", "BUY_NO", "HOLD"}:
        raise ValueError("action must be BUY_YES, BUY_NO, or HOLD")
    if not isinstance(row["model_diagnostics"], dict):
        raise ValueError("model_diagnostics must be an object")
    if not isinstance(row["reasons"], list):
        raise ValueError("reasons must be a list")
    if not isinstance(row["warnings"], list):
        raise ValueError("warnings must be a list")


def _probability(name: str, value: object) -> None:
    """Validate a probability-like field."""
    number = float(value)
    if not 0.0 <= number <= 1.0:
        raise ValueError(f"{name} must be between 0 and 1")
