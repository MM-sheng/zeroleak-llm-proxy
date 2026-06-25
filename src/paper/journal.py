"""Local JSONL journal for paper trading records."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from src.paper.paper_executor import PaperExecution


JOURNAL_FIELDS: tuple[str, ...] = (
    "timestamp_utc",
    "market_id",
    "question",
    "action",
    "side",
    "entry_price",
    "model_probability",
    "edge",
    "size_usd",
    "rationale",
    "current_price",
    "mark_to_market_pnl",
    "final_resolution",
    "realized_pnl",
    "lesson",
)


@dataclass(frozen=True)
class PaperTradeJournal:
    """Append-only JSONL storage for simulated paper trades."""

    path: Path

    def append(self, entry: PaperExecution | Mapping[str, object]) -> dict[str, object]:
        """Append one paper trade entry and return the normalized row."""
        row = normalize_journal_entry(entry)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
        return row

    def read_all(self) -> list[dict[str, object]]:
        """Read all journal rows in insertion order."""
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
                    raise ValueError(f"invalid journal JSON on line {line_number}") from exc
                if not isinstance(payload, dict):
                    raise ValueError(f"journal row {line_number} must be an object")
                rows.append(normalize_journal_entry(payload))
        return rows


def append_journal_entry(path: str | Path, entry: PaperExecution | Mapping[str, object]) -> dict[str, object]:
    """Append a paper trade entry to a JSONL journal."""
    return PaperTradeJournal(Path(path)).append(entry)


def read_journal(path: str | Path) -> list[dict[str, object]]:
    """Read a paper trade journal from disk."""
    return PaperTradeJournal(Path(path)).read_all()


def normalize_journal_entry(entry: PaperExecution | Mapping[str, object]) -> dict[str, object]:
    """Normalize an execution or mapping to the project journal schema."""
    source = entry.as_journal_row() if isinstance(entry, PaperExecution) else dict(entry)
    missing = [field for field in JOURNAL_FIELDS if field not in source]
    if missing:
        raise ValueError(f"journal entry missing fields: {', '.join(missing)}")
    normalized = {field: source[field] for field in JOURNAL_FIELDS}
    _validate_entry(normalized)
    return normalized


def _validate_entry(entry: Mapping[str, object]) -> None:
    """Validate the journal fields that protect paper-trading invariants."""
    if not str(entry["timestamp_utc"]).strip():
        raise ValueError("timestamp_utc is required")
    if not str(entry["market_id"]).strip():
        raise ValueError("market_id is required")
    if not str(entry["question"]).strip():
        raise ValueError("question is required")
    if entry["action"] not in {"BUY_YES", "BUY_NO", "HOLD"}:
        raise ValueError("action must be BUY_YES, BUY_NO, or HOLD")
    if entry["side"] not in {"YES", "NO", "NONE"}:
        raise ValueError("side must be YES, NO, or NONE")
    for field in ("model_probability", "edge", "size_usd", "mark_to_market_pnl"):
        float(entry[field])
    if entry["entry_price"] is not None:
        _probability("entry_price", entry["entry_price"])
    if entry["current_price"] is not None:
        _probability("current_price", entry["current_price"])
    _probability("model_probability", entry["model_probability"])
    if not isinstance(entry["rationale"], list):
        raise ValueError("rationale must be a list")


def _probability(name: str, value: object) -> None:
    """Validate probability-like fields."""
    number = float(value)
    if not 0.0 <= number <= 1.0:
        raise ValueError(f"{name} must be between 0 and 1")
