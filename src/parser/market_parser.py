"""Market question parser domain models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import re
from typing import Literal


Direction = Literal["above", "below", "unknown"]
EventType = Literal["touch", "terminal", "unknown"]

VALID_DIRECTIONS = {"above", "below", "unknown"}
VALID_EVENT_TYPES = {"touch", "terminal", "unknown"}
MONTHS = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}


@dataclass(frozen=True)
class ParsedMarket:
    """Structured representation of a parsed BTC market question."""

    asset: str = "unknown"
    target_price: float | None = None
    direction: Direction = "unknown"
    event_type: EventType = "unknown"
    deadline_utc: datetime | None = None
    confidence: float = 0.0
    warnings: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        """Validate parser output without inferring parse semantics."""
        stripped_asset = self.asset.strip()
        normalized_asset = stripped_asset.upper() if stripped_asset and stripped_asset.lower() != "unknown" else "unknown"
        object.__setattr__(self, "asset", normalized_asset)

        if self.target_price is not None:
            target_price = float(self.target_price)
            if target_price <= 0:
                raise ValueError("target_price must be positive when present")
            object.__setattr__(self, "target_price", target_price)

        if self.direction not in VALID_DIRECTIONS:
            raise ValueError(f"direction must be one of {sorted(VALID_DIRECTIONS)}")
        if self.event_type not in VALID_EVENT_TYPES:
            raise ValueError(f"event_type must be one of {sorted(VALID_EVENT_TYPES)}")

        confidence = float(self.confidence)
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        object.__setattr__(self, "confidence", confidence)

        if self.deadline_utc is not None:
            deadline = self.deadline_utc
            if deadline.tzinfo is None:
                deadline = deadline.replace(tzinfo=timezone.utc)
            else:
                deadline = deadline.astimezone(timezone.utc)
            object.__setattr__(self, "deadline_utc", deadline)

        object.__setattr__(self, "warnings", tuple(str(warning) for warning in self.warnings))


def parse_market_question(
    question: str,
    *,
    reference_time_utc: datetime | None = None,
) -> ParsedMarket:
    """Parse common BTC Polymarket question fields without model inference."""
    if not isinstance(question, str) or not question.strip():
        raise ValueError("question must be a non-empty string")

    reference = _coerce_reference_time(reference_time_utc)
    normalized = question.strip()
    lowered = normalized.lower()
    warnings: list[str] = []

    asset = _parse_asset(lowered)
    if asset == "unknown":
        warnings.append("asset_not_detected")

    target_price = _parse_target_price(lowered)
    if target_price is None:
        warnings.append("target_price_not_detected")

    direction = _parse_direction(lowered)
    if direction == "unknown":
        warnings.append("direction_not_detected")

    event_type, event_warnings = _parse_event_type(lowered)
    warnings.extend(event_warnings)
    if event_type == "unknown":
        warnings.append("event_type_not_detected")

    deadline = _parse_deadline_utc(lowered, reference)
    if deadline is None:
        warnings.append("deadline_not_detected")

    confidence = _confidence_score(
        asset=asset,
        target_price=target_price,
        direction=direction,
        event_type=event_type,
        deadline_utc=deadline,
    )
    return ParsedMarket(
        asset=asset,
        target_price=target_price,
        direction=direction,
        event_type=event_type,
        deadline_utc=deadline,
        confidence=confidence,
        warnings=tuple(warnings),
    )


def _coerce_reference_time(reference_time_utc: datetime | None) -> datetime:
    """Return an aware UTC reference time for relative parse choices."""
    reference = reference_time_utc or datetime.now(timezone.utc)
    if reference.tzinfo is None:
        return reference.replace(tzinfo=timezone.utc)
    return reference.astimezone(timezone.utc)


def _parse_asset(text: str) -> str:
    """Parse supported market asset symbols."""
    if re.search(r"\b(bitcoin|btc|xbt)\b", text):
        return "BTC"
    return "unknown"


def _parse_target_price(text: str) -> float | None:
    """Parse common USD target price forms such as $120,000 or 120k."""
    money_match = re.search(r"\$\s*([0-9][0-9,]*(?:\.\d+)?)\s*([kKmM])?", text)
    if money_match:
        return _coerce_price_match(money_match)

    contextual_match = re.search(
        r"\b(?:above|over|below|under|hit|hits|reach|reaches|touch|touches|"
        r"exceed|exceeds|greater than|less than|at least|at most)\s+"
        r"([0-9][0-9,]*(?:\.\d+)?)\s*([kKmM])?\b",
        text,
    )
    if contextual_match:
        return _coerce_price_match(contextual_match)
    return None


def _coerce_price_match(match: re.Match[str]) -> float | None:
    """Convert a regex price match into a positive USD float."""
    raw_number = match.group(1).replace(",", "")
    multiplier = {"k": 1_000.0, "m": 1_000_000.0}.get((match.group(2) or "").lower(), 1.0)
    price = float(raw_number) * multiplier
    return price if price > 0 else None


def _parse_direction(text: str) -> Direction:
    """Parse above/below direction terms."""
    if re.search(r"\b(above|over|greater than|at least|exceed|exceeds)\b", text):
        return "above"
    if re.search(r"\b(below|under|less than|at most)\b", text):
        return "below"
    return "unknown"


def _parse_event_type(text: str) -> tuple[EventType, tuple[str, ...]]:
    """Parse whether a market is about terminal settlement or path touch."""
    has_terminal_evidence = bool(
        re.search(r"\b(close|closes|closing|finish|finishes|settle|settles|end|ends)\b", text)
        or re.search(r"\bbe\s+(?:above|over|below|under)\b", text)
        or re.search(r"\bbe\s+(?:at least|at most|greater than|less than)\b", text)
    )
    has_touch_evidence = bool(
        re.search(r"\b(hit|hits|reach|reaches|touch|touches|exceed|exceeds)\b", text)
        or re.search(r"\btrade(?:s)?\s+(?:above|over|below|under)\b", text)
    )

    if has_terminal_evidence and has_touch_evidence:
        return "terminal", ("event_type_conflict_terminal_preferred",)
    if has_terminal_evidence:
        return "terminal", ()
    if has_touch_evidence:
        return "touch", ()
    return "unknown", ()


def _parse_deadline_utc(text: str, reference_time_utc: datetime) -> datetime | None:
    """Parse month-day deadlines into UTC end-of-day timestamps."""
    month_names = "|".join(sorted(MONTHS, key=len, reverse=True))
    match = re.search(
        rf"\b({month_names})\.?\s+([0-9]{{1,2}})(?:st|nd|rd|th)?(?:,?\s+([0-9]{{4}}))?\b",
        text,
    )
    if not match:
        numeric_match = re.search(r"\b([0-9]{1,2})/([0-9]{1,2})(?:/([0-9]{2,4}))?\b", text)
        if not numeric_match:
            return None
        month = int(numeric_match.group(1))
        day = int(numeric_match.group(2))
        raw_year = numeric_match.group(3)
        year = reference_time_utc.year if raw_year is None else int(raw_year)
        if raw_year is not None and year < 100:
            year += 2000
        return _build_deadline_utc(year=year, month=month, day=day, reference_time_utc=reference_time_utc, has_year=raw_year is not None)

    month = MONTHS[match.group(1).rstrip(".")]
    day = int(match.group(2))
    year = int(match.group(3)) if match.group(3) else reference_time_utc.year
    return _build_deadline_utc(
        year=year,
        month=month,
        day=day,
        reference_time_utc=reference_time_utc,
        has_year=match.group(3) is not None,
    )


def _build_deadline_utc(
    *,
    year: int,
    month: int,
    day: int,
    reference_time_utc: datetime,
    has_year: bool,
) -> datetime | None:
    """Build a UTC end-of-day deadline and roll yearless past dates forward."""
    try:
        deadline = datetime(year, month, day, 23, 59, 59, tzinfo=timezone.utc)
    except ValueError:
        return None
    if not has_year and deadline < reference_time_utc:
        deadline = datetime(year + 1, month, day, 23, 59, 59, tzinfo=timezone.utc)
    return deadline


def _confidence_score(
    *,
    asset: str,
    target_price: float | None,
    direction: Direction,
    event_type: EventType,
    deadline_utc: datetime | None,
) -> float:
    """Compute a simple field-completeness confidence score."""
    score = 0.0
    score += 0.20 if asset != "unknown" else 0.0
    score += 0.25 if target_price is not None else 0.0
    score += 0.20 if direction != "unknown" else 0.0
    score += 0.15 if event_type != "unknown" else 0.0
    score += 0.20 if deadline_utc is not None else 0.0
    return round(score, 2)
