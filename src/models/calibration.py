"""Historical prediction storage for model calibration."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping


HISTORICAL_PREDICTION_FIELDS: tuple[str, ...] = (
    "timestamp_utc",
    "market_id",
    "question",
    "model_name",
    "probability",
    "event_type",
    "deadline_utc",
    "target_price",
    "direction",
    "market_price",
    "outcome",
    "resolved_at_utc",
    "metadata",
)


@dataclass(frozen=True)
class HistoricalPrediction:
    """One timestamped model probability saved for future calibration."""

    timestamp_utc: datetime
    market_id: str
    question: str
    model_name: str
    probability: float
    event_type: str
    deadline_utc: datetime | None = None
    target_price: float | None = None
    direction: str = "unknown"
    market_price: float | None = None
    outcome: float | None = None
    resolved_at_utc: datetime | None = None
    metadata: Mapping[str, object] = field(default_factory=dict)

    @classmethod
    def from_recommendation(
        cls,
        recommendation: Mapping[str, object],
        *,
        event_type: str,
        deadline_utc: datetime | None = None,
        target_price: float | None = None,
        direction: str = "unknown",
        market_price: float | None = None,
        outcome: float | None = None,
        resolved_at_utc: datetime | None = None,
        metadata: Mapping[str, object] | None = None,
    ) -> "HistoricalPrediction":
        """Build a calibration prediction record from a saved recommendation row."""
        return cls(
            timestamp_utc=_parse_timestamp(recommendation["timestamp_utc"]),
            market_id=str(recommendation["market_id"]),
            question=str(recommendation["question"]),
            model_name=str(recommendation["model_name"]),
            probability=float(recommendation["model_probability"]),
            event_type=event_type,
            deadline_utc=deadline_utc,
            target_price=target_price,
            direction=direction,
            market_price=market_price,
            outcome=outcome,
            resolved_at_utc=resolved_at_utc,
            metadata=metadata or {},
        )

    def as_dict(self) -> dict[str, object]:
        """Return the canonical JSONL row for this historical prediction."""
        row: dict[str, object] = {
            "timestamp_utc": _normalize_timestamp(self.timestamp_utc).isoformat(),
            "market_id": self.market_id,
            "question": self.question,
            "model_name": self.model_name,
            "probability": float(self.probability),
            "event_type": self.event_type,
            "deadline_utc": _optional_timestamp(self.deadline_utc),
            "target_price": self.target_price,
            "direction": self.direction,
            "market_price": self.market_price,
            "outcome": self.outcome,
            "resolved_at_utc": _optional_timestamp(self.resolved_at_utc),
            "metadata": dict(self.metadata),
        }
        _validate_prediction_row(row)
        return row


@dataclass(frozen=True)
class HistoricalPredictionLog:
    """Append-only JSONL store for calibration prediction records."""

    path: Path

    def append(self, record: HistoricalPrediction | Mapping[str, object]) -> dict[str, object]:
        """Append one prediction record and return the normalized row."""
        row = normalize_historical_prediction(record)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
        return row

    def read_all(self) -> list[dict[str, object]]:
        """Read all saved historical prediction rows."""
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
                    raise ValueError(f"invalid historical prediction JSON on line {line_number}") from exc
                if not isinstance(payload, dict):
                    raise ValueError(f"historical prediction row {line_number} must be an object")
                rows.append(normalize_historical_prediction(payload))
        return rows


@dataclass(frozen=True)
class BrierScoreResult:
    """Brier score summary for resolved historical predictions."""

    score: float
    resolved_count: int
    skipped_unresolved_count: int


@dataclass(frozen=True)
class LogLossResult:
    """Log loss summary for resolved historical predictions."""

    loss: float
    resolved_count: int
    skipped_unresolved_count: int
    clipped_probability_count: int


@dataclass(frozen=True)
class CalibrationCurveBucket:
    """One probability bucket in a calibration curve."""

    lower_bound: float
    upper_bound: float
    count: int
    mean_predicted_probability: float | None
    observed_frequency: float | None


@dataclass(frozen=True)
class CalibrationCurveResult:
    """Calibration curve buckets built from resolved historical predictions."""

    buckets: tuple[CalibrationCurveBucket, ...]
    resolved_count: int
    skipped_unresolved_count: int


@dataclass(frozen=True)
class BucketHitRateCheck:
    """Observed hit-rate check for one probability bucket."""

    lower_bound: float
    upper_bound: float
    count: int
    mean_predicted_probability: float | None
    observed_frequency: float | None
    calibration_gap: float | None
    absolute_gap: float | None
    status: str


@dataclass(frozen=True)
class HitRateCheckResult:
    """Bucket-level realized hit-rate diagnostics."""

    buckets: tuple[BucketHitRateCheck, ...]
    resolved_count: int
    skipped_unresolved_count: int
    checked_bucket_count: int
    insufficient_bucket_count: int
    flagged_bucket_count: int


def save_historical_prediction(
    path: str | Path,
    record: HistoricalPrediction | Mapping[str, object],
) -> dict[str, object]:
    """Save one historical prediction record."""
    return HistoricalPredictionLog(Path(path)).append(record)


def read_historical_predictions(path: str | Path) -> list[dict[str, object]]:
    """Read saved historical prediction records."""
    return HistoricalPredictionLog(Path(path)).read_all()


def calculate_brier_score(records: list[Mapping[str, object]]) -> BrierScoreResult:
    """Calculate Brier score from historical prediction rows with known outcomes."""
    squared_errors: list[float] = []
    skipped_unresolved_count = 0
    for record in records:
        row = normalize_historical_prediction(record)
        if row["outcome"] is None:
            skipped_unresolved_count += 1
            continue
        probability = float(row["probability"])
        outcome = float(row["outcome"])
        squared_errors.append((probability - outcome) ** 2)
    if not squared_errors:
        raise ValueError("Brier score requires at least one resolved prediction")
    return BrierScoreResult(
        score=sum(squared_errors) / len(squared_errors),
        resolved_count=len(squared_errors),
        skipped_unresolved_count=skipped_unresolved_count,
    )


def calculate_log_loss(records: list[Mapping[str, object]], epsilon: float = 1e-15) -> LogLossResult:
    """Calculate binary log loss from historical prediction rows with known outcomes."""
    if not 0.0 < epsilon < 0.5:
        raise ValueError("epsilon must be greater than 0 and less than 0.5")
    losses: list[float] = []
    skipped_unresolved_count = 0
    clipped_probability_count = 0
    for record in records:
        row = normalize_historical_prediction(record)
        if row["outcome"] is None:
            skipped_unresolved_count += 1
            continue
        probability = float(row["probability"])
        clipped_probability = min(max(probability, epsilon), 1.0 - epsilon)
        if clipped_probability != probability:
            clipped_probability_count += 1
        outcome = float(row["outcome"])
        losses.append(-((outcome * math.log(clipped_probability)) + ((1.0 - outcome) * math.log(1.0 - clipped_probability))))
    if not losses:
        raise ValueError("Log loss requires at least one resolved prediction")
    return LogLossResult(
        loss=sum(losses) / len(losses),
        resolved_count=len(losses),
        skipped_unresolved_count=skipped_unresolved_count,
        clipped_probability_count=clipped_probability_count,
    )


def generate_calibration_curve(
    records: list[Mapping[str, object]],
    bin_count: int = 10,
) -> CalibrationCurveResult:
    """Generate probability bucket data for a calibration curve."""
    if bin_count <= 0:
        raise ValueError("bin_count must be positive")
    bucket_probabilities: list[list[float]] = [[] for _ in range(bin_count)]
    bucket_outcomes: list[list[float]] = [[] for _ in range(bin_count)]
    skipped_unresolved_count = 0
    for record in records:
        row = normalize_historical_prediction(record)
        if row["outcome"] is None:
            skipped_unresolved_count += 1
            continue
        probability = float(row["probability"])
        outcome = float(row["outcome"])
        index = min(int(probability * bin_count), bin_count - 1)
        bucket_probabilities[index].append(probability)
        bucket_outcomes[index].append(outcome)
    resolved_count = sum(len(values) for values in bucket_probabilities)
    if resolved_count == 0:
        raise ValueError("Calibration curve requires at least one resolved prediction")
    buckets: list[CalibrationCurveBucket] = []
    for index in range(bin_count):
        probabilities = bucket_probabilities[index]
        outcomes = bucket_outcomes[index]
        lower_bound = index / bin_count
        upper_bound = (index + 1) / bin_count
        if probabilities:
            mean_probability = sum(probabilities) / len(probabilities)
            observed_frequency = sum(outcomes) / len(outcomes)
        else:
            mean_probability = None
            observed_frequency = None
        buckets.append(
            CalibrationCurveBucket(
                lower_bound=lower_bound,
                upper_bound=upper_bound,
                count=len(probabilities),
                mean_predicted_probability=mean_probability,
                observed_frequency=observed_frequency,
            )
        )
    return CalibrationCurveResult(
        buckets=tuple(buckets),
        resolved_count=resolved_count,
        skipped_unresolved_count=skipped_unresolved_count,
    )


def check_realized_hit_rate_by_probability_bucket(
    records: list[Mapping[str, object]],
    bin_count: int = 10,
    min_bucket_count: int = 5,
    max_abs_gap: float = 0.20,
) -> HitRateCheckResult:
    """Check realized hit rates against mean predicted probabilities by bucket."""
    if min_bucket_count <= 0:
        raise ValueError("min_bucket_count must be positive")
    if not 0.0 <= max_abs_gap <= 1.0:
        raise ValueError("max_abs_gap must be between 0 and 1")
    curve = generate_calibration_curve(records, bin_count=bin_count)
    checks: list[BucketHitRateCheck] = []
    checked_bucket_count = 0
    insufficient_bucket_count = 0
    flagged_bucket_count = 0
    for bucket in curve.buckets:
        if bucket.count < min_bucket_count:
            calibration_gap = None
            absolute_gap = None
            status = "insufficient_data"
            insufficient_bucket_count += 1
        else:
            checked_bucket_count += 1
            assert bucket.mean_predicted_probability is not None
            assert bucket.observed_frequency is not None
            calibration_gap = bucket.observed_frequency - bucket.mean_predicted_probability
            absolute_gap = abs(calibration_gap)
            if absolute_gap > max_abs_gap:
                status = "miscalibrated"
                flagged_bucket_count += 1
            else:
                status = "calibrated"
        checks.append(
            BucketHitRateCheck(
                lower_bound=bucket.lower_bound,
                upper_bound=bucket.upper_bound,
                count=bucket.count,
                mean_predicted_probability=bucket.mean_predicted_probability,
                observed_frequency=bucket.observed_frequency,
                calibration_gap=calibration_gap,
                absolute_gap=absolute_gap,
                status=status,
            )
        )
    return HitRateCheckResult(
        buckets=tuple(checks),
        resolved_count=curve.resolved_count,
        skipped_unresolved_count=curve.skipped_unresolved_count,
        checked_bucket_count=checked_bucket_count,
        insufficient_bucket_count=insufficient_bucket_count,
        flagged_bucket_count=flagged_bucket_count,
    )


def normalize_historical_prediction(record: HistoricalPrediction | Mapping[str, object]) -> dict[str, object]:
    """Normalize a prediction record to the canonical calibration schema."""
    source = record.as_dict() if isinstance(record, HistoricalPrediction) else dict(record)
    missing = [field for field in HISTORICAL_PREDICTION_FIELDS if field not in source]
    if missing:
        raise ValueError(f"historical prediction missing fields: {', '.join(missing)}")
    normalized = {field: source[field] for field in HISTORICAL_PREDICTION_FIELDS}
    _validate_prediction_row(normalized)
    return normalized


def _normalize_timestamp(timestamp: datetime) -> datetime:
    """Return a timezone-aware UTC timestamp."""
    if timestamp.tzinfo is None:
        raise ValueError("timestamp_utc must be timezone-aware")
    return timestamp.astimezone(timezone.utc)


def _optional_timestamp(timestamp: datetime | None) -> str | None:
    """Return an optional UTC ISO timestamp."""
    if timestamp is None:
        return None
    return _normalize_timestamp(timestamp).isoformat()


def _parse_timestamp(value: object) -> datetime:
    """Parse a timezone-aware timestamp from an existing record."""
    if isinstance(value, datetime):
        return _normalize_timestamp(value)
    timestamp = datetime.fromisoformat(str(value))
    return _normalize_timestamp(timestamp)


def _validate_prediction_row(row: Mapping[str, object]) -> None:
    """Validate prediction rows before writing or reading."""
    if not str(row["timestamp_utc"]).strip():
        raise ValueError("timestamp_utc is required")
    for field_name in ("market_id", "question", "model_name"):
        if not str(row[field_name]).strip():
            raise ValueError(f"{field_name} is required")
    _probability("probability", row["probability"])
    if row["market_price"] is not None:
        _probability("market_price", row["market_price"])
    if row["outcome"] is not None:
        _probability("outcome", row["outcome"])
    if row["target_price"] is not None and float(row["target_price"]) <= 0.0:
        raise ValueError("target_price must be positive")
    if row["event_type"] not in {"touch", "terminal", "unknown"}:
        raise ValueError("event_type must be touch, terminal, or unknown")
    if row["direction"] not in {"above", "below", "unknown"}:
        raise ValueError("direction must be above, below, or unknown")
    if not isinstance(row["metadata"], dict):
        raise ValueError("metadata must be an object")


def _probability(name: str, value: object) -> None:
    """Validate a probability-like numeric field."""
    number = float(value)
    if not 0.0 <= number <= 1.0:
        raise ValueError(f"{name} must be between 0 and 1")
