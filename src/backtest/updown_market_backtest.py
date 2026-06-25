"""Read-only BTC Up/Down market data helpers for paper backtests."""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable, Optional

import requests

from src.backtest.metrics import BacktestMetrics, calculate_binary_trade_pnl, summarize_backtest_metrics


@dataclass(frozen=True)
class UpDownWindow:
    """One Polymarket BTC Up/Down market window."""

    kind: str
    slug: str
    condition_id: str
    start_time_utc: datetime
    end_time_utc: datetime
    outcome_token_ids: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class UpDownTrade:
    """One historical Up/Down market trade."""

    condition_id: str
    timestamp_utc: datetime
    outcome: str
    side: str
    price: float
    size: float


@dataclass(frozen=True)
class UpDownPricePoint:
    """One historical CLOB price point for an Up/Down outcome token."""

    outcome: str
    timestamp_utc: datetime
    price: float


@dataclass(frozen=True)
class BTCCandle:
    """One BTC/USD one-minute candle used for approximate Up/Down resolution."""

    timestamp_utc: datetime
    open: float
    close: float


@dataclass(frozen=True)
class UpDownResolution:
    """Approximate Up/Down market resolution from BTC candles."""

    slug: str
    winner: str
    start_price: float
    end_price: float


@dataclass(frozen=True)
class UpDownBacktestEntry:
    """One simulated paper entry from a historical Up/Down trade."""

    slug: str
    kind: str
    policy: str
    outcome: str
    winner: str
    entry_price: float
    size_usd: float
    pnl_usd: float
    entry_time_utc: datetime


@dataclass(frozen=True)
class CachedUpDownBacktestResult:
    """Result from a cached read-only Up/Down paper backtest run."""

    windows: tuple[UpDownWindow, ...]
    entries: tuple[UpDownBacktestEntry, ...]
    metrics: BacktestMetrics
    skipped_windows: int = 0


EventFetcher = Callable[[str], Optional[Mapping[str, object]]]
TradesFetcher = Callable[[str], list[Mapping[str, object]]]
PriceHistoryFetcher = Callable[[str, datetime, datetime], list[Mapping[str, object]]]
CandleFetcher = Callable[[datetime, datetime], list[BTCCandle]]
UPDOWN_ENTRY_POLICIES = ("first_seen", "first_start_window", "last_before_end")
UPDOWN_DATA_SOURCES = ("trades", "price_history")


def build_recent_updown_slugs(
    *,
    now_utc: datetime,
    lookback_minutes: int = 180,
    include_15m: bool = True,
) -> list[tuple[str, datetime, datetime, str]]:
    """Build recent BTC Up/Down event slugs from their timestamp pattern."""
    if now_utc.tzinfo is None:
        raise ValueError("now_utc must be timezone-aware")
    if lookback_minutes <= 0:
        raise ValueError("lookback_minutes must be positive")
    now_ts = int(now_utc.astimezone(timezone.utc).timestamp())
    aligned_ts = now_ts - (now_ts % 300)
    start_floor = aligned_ts - (lookback_minutes * 60)
    specs: list[tuple[str, datetime, datetime, str]] = []
    for start_ts in range(aligned_ts - 300, start_floor - 1, -300):
        end_ts = start_ts + 300
        if end_ts < now_ts:
            specs.append(_slug_spec("5m", start_ts, end_ts))
        if include_15m and start_ts % 900 == 0:
            end_15m = start_ts + 900
            if end_15m < now_ts:
                specs.append(_slug_spec("15m", start_ts, end_15m))
    return specs


def window_from_gamma_event(
    event: Mapping[str, object],
    *,
    kind: str,
    start_time_utc: datetime,
    end_time_utc: datetime,
    slug: str,
) -> UpDownWindow:
    """Extract one Up/Down window from a Gamma event response."""
    markets = event.get("markets")
    if not isinstance(markets, list) or not markets:
        raise ValueError("Gamma event does not contain markets")
    first_market = markets[0]
    if not isinstance(first_market, Mapping):
        raise ValueError("Gamma event market must be an object")
    condition_id = str(first_market.get("conditionId") or "").strip()
    if not condition_id:
        raise ValueError("Gamma event market missing conditionId")
    outcome_token_ids = _extract_outcome_token_ids(first_market)
    return UpDownWindow(
        kind=kind,
        slug=slug,
        condition_id=condition_id,
        start_time_utc=_coerce_utc(start_time_utc),
        end_time_utc=_coerce_utc(end_time_utc),
        outcome_token_ids=outcome_token_ids,
    )


def parse_updown_trades(raw_trades: Iterable[Mapping[str, object]], *, condition_id: str) -> list[UpDownTrade]:
    """Normalize Data API trade rows for one Up/Down condition."""
    trades: list[UpDownTrade] = []
    for row in raw_trades:
        outcome = str(row.get("outcome") or "").strip()
        if outcome not in {"Up", "Down"}:
            continue
        price = float(row["price"])
        if not 0.0 < price < 1.0:
            continue
        trades.append(
            UpDownTrade(
                condition_id=condition_id,
                timestamp_utc=datetime.fromtimestamp(int(row["timestamp"]), timezone.utc),
                outcome=outcome,
                side=str(row.get("side") or ""),
                price=price,
                size=float(row.get("size") or 0.0),
            )
        )
    return sorted(trades, key=lambda trade: trade.timestamp_utc)


def parse_price_history(
    raw_history: Mapping[str, object],
    *,
    outcome: str,
) -> list[UpDownPricePoint]:
    """Normalize CLOB price history rows for one Up/Down outcome token."""
    history = raw_history.get("history")
    if not isinstance(history, list):
        raise ValueError("CLOB price history response must contain a history list")
    points: list[UpDownPricePoint] = []
    for row in history:
        if not isinstance(row, Mapping):
            continue
        price = float(row["p"])
        if not 0.0 < price < 1.0:
            continue
        points.append(
            UpDownPricePoint(
                outcome=outcome,
                timestamp_utc=datetime.fromtimestamp(int(row["t"]), timezone.utc),
                price=price,
            )
        )
    return sorted(points, key=lambda point: point.timestamp_utc)


def parse_coinbase_candles(raw_candles: Iterable[Iterable[object]]) -> list[BTCCandle]:
    """Normalize Coinbase candle rows of [time, low, high, open, close, volume]."""
    candles: list[BTCCandle] = []
    for row in raw_candles:
        values = list(row)
        if len(values) < 5:
            raise ValueError("Coinbase candle row must contain at least five fields")
        candles.append(
            BTCCandle(
                timestamp_utc=datetime.fromtimestamp(int(values[0]), timezone.utc),
                open=float(values[3]),
                close=float(values[4]),
            )
        )
    return sorted(candles, key=lambda candle: candle.timestamp_utc)


def resolve_updown_window(window: UpDownWindow, candles: Iterable[BTCCandle]) -> UpDownResolution:
    """Resolve one Up/Down window from candles available through the window end."""
    relevant = [
        candle
        for candle in candles
        if window.start_time_utc <= candle.timestamp_utc <= window.end_time_utc
    ]
    if not relevant:
        raise ValueError(f"no BTC candles available for {window.slug}")
    start_price = relevant[0].open
    end_price = relevant[-1].close
    return UpDownResolution(
        slug=window.slug,
        winner="Up" if end_price >= start_price else "Down",
        start_price=start_price,
        end_price=end_price,
    )


def simulate_updown_entries(
    *,
    window: UpDownWindow,
    trades: Iterable[UpDownTrade],
    resolution: UpDownResolution,
    size_usd: float = 10.0,
    policies: tuple[str, ...] = UPDOWN_ENTRY_POLICIES,
) -> list[UpDownBacktestEntry]:
    """Simulate paper entries from historical Up/Down trades without future data."""
    if size_usd < 0.0:
        raise ValueError("size_usd must be non-negative")
    _validate_updown_policies(policies)
    sorted_trades = sorted(trades, key=lambda trade: trade.timestamp_utc)
    selected: dict[tuple[str, str], UpDownTrade] = {}
    window_duration = window.end_time_utc - window.start_time_utc
    start_window_end = window.start_time_utc + min(window_duration / 5, timedelta(seconds=90))
    for trade in sorted_trades:
        if "first_seen" in policies:
            selected.setdefault(("first_seen", trade.outcome), trade)
        if "first_start_window" in policies and window.start_time_utc <= trade.timestamp_utc <= start_window_end:
            selected.setdefault(("first_start_window", trade.outcome), trade)
        if "last_before_end" in policies and trade.timestamp_utc <= window.end_time_utc:
            selected[("last_before_end", trade.outcome)] = trade
    entries: list[UpDownBacktestEntry] = []
    for (policy, outcome), trade in sorted(selected.items()):
        entries.append(
            UpDownBacktestEntry(
                slug=window.slug,
                kind=window.kind,
                policy=policy,
                outcome=outcome,
                winner=resolution.winner,
                entry_price=trade.price,
                size_usd=size_usd,
                pnl_usd=calculate_binary_trade_pnl(
                    side="BUY_YES",
                    entry_price=trade.price,
                    size_usd=size_usd,
                    resolved_yes=outcome == resolution.winner,
                ),
                entry_time_utc=trade.timestamp_utc,
            )
        )
    return entries


def simulate_updown_price_entries(
    *,
    window: UpDownWindow,
    price_points: Iterable[UpDownPricePoint],
    resolution: UpDownResolution,
    size_usd: float = 10.0,
    policies: tuple[str, ...] = UPDOWN_ENTRY_POLICIES,
) -> list[UpDownBacktestEntry]:
    """Simulate paper entries from historical CLOB price points without future data."""
    if size_usd < 0.0:
        raise ValueError("size_usd must be non-negative")
    _validate_updown_policies(policies)
    sorted_points = sorted(price_points, key=lambda point: point.timestamp_utc)
    selected: dict[tuple[str, str], UpDownPricePoint] = {}
    window_duration = window.end_time_utc - window.start_time_utc
    start_window_end = window.start_time_utc + min(window_duration / 5, timedelta(seconds=90))
    for point in sorted_points:
        if "first_seen" in policies:
            selected.setdefault(("first_seen", point.outcome), point)
        if "first_start_window" in policies and window.start_time_utc <= point.timestamp_utc <= start_window_end:
            selected.setdefault(("first_start_window", point.outcome), point)
        if "last_before_end" in policies and point.timestamp_utc <= window.end_time_utc:
            selected[("last_before_end", point.outcome)] = point
    entries: list[UpDownBacktestEntry] = []
    for (policy, outcome), point in sorted(selected.items()):
        entries.append(
            UpDownBacktestEntry(
                slug=window.slug,
                kind=window.kind,
                policy=policy,
                outcome=outcome,
                winner=resolution.winner,
                entry_price=point.price,
                size_usd=size_usd,
                pnl_usd=calculate_binary_trade_pnl(
                    side="BUY_YES",
                    entry_price=point.price,
                    size_usd=size_usd,
                    resolved_yes=outcome == resolution.winner,
                ),
                entry_time_utc=point.timestamp_utc,
            )
        )
    return entries


def summarize_updown_entries(
    entries: Iterable[UpDownBacktestEntry],
    *,
    initial_bankroll_usd: float = 1000.0,
) -> BacktestMetrics:
    """Summarize Up/Down paper entries with existing backtest metrics."""
    rows = list(entries)
    return summarize_backtest_metrics(
        [entry.pnl_usd for entry in rows],
        initial_bankroll_usd=initial_bankroll_usd,
        exposures_usd=[entry.size_usd for entry in rows],
    )


def summarize_updown_entries_by_group(
    entries: Iterable[UpDownBacktestEntry],
    *,
    group_by: str,
    initial_bankroll_usd: float = 1000.0,
) -> dict[str, BacktestMetrics]:
    """Summarize Up/Down paper entries grouped by policy, kind, outcome, or winner."""
    if group_by not in {"policy", "kind", "outcome", "winner"}:
        raise ValueError("group_by must be policy, kind, outcome, or winner")
    groups: dict[str, list[UpDownBacktestEntry]] = {}
    for entry in entries:
        key = str(getattr(entry, group_by))
        groups.setdefault(key, []).append(entry)
    return {
        key: summarize_updown_entries(rows, initial_bankroll_usd=initial_bankroll_usd)
        for key, rows in sorted(groups.items())
    }


def run_cached_updown_backtest(
    *,
    cache_dir: str | Path,
    now_utc: datetime,
    lookback_minutes: int = 180,
    include_15m: bool = True,
    size_usd: float = 10.0,
    initial_bankroll_usd: float = 1000.0,
    policies: tuple[str, ...] = UPDOWN_ENTRY_POLICIES,
    data_source: str = "trades",
    event_fetcher: EventFetcher | None = None,
    trades_fetcher: TradesFetcher | None = None,
    price_history_fetcher: PriceHistoryFetcher | None = None,
    candle_fetcher: CandleFetcher | None = None,
) -> CachedUpDownBacktestResult:
    """Run a cached read-only BTC Up/Down paper backtest."""
    _validate_updown_policies(policies)
    _validate_updown_data_source(data_source)
    root = Path(cache_dir)
    specs = build_recent_updown_slugs(
        now_utc=now_utc,
        lookback_minutes=lookback_minutes,
        include_15m=include_15m,
    )
    fetch_event = event_fetcher or (lambda slug: fetch_gamma_event_by_slug(slug))
    fetch_trades = trades_fetcher or (lambda condition_id: fetch_data_api_trades(condition_id))
    fetch_price_history = price_history_fetcher or (
        lambda token_id, start_time_utc, end_time_utc: fetch_clob_price_history(
            token_id=token_id,
            start_time_utc=start_time_utc,
            end_time_utc=end_time_utc,
        )
    )
    fetch_candles = candle_fetcher or (
        lambda start_time_utc, end_time_utc: fetch_coinbase_candles(
            start_time_utc=start_time_utc,
            end_time_utc=end_time_utc,
        )
    )

    windows: list[UpDownWindow] = []
    skipped_windows = 0
    for kind, start_time, end_time, slug in specs:
        try:
            event = _cached_json(root / "events" / f"{slug}.json", lambda slug=slug: fetch_event(slug))
        except (requests.RequestException, ValueError, TypeError, OSError):
            skipped_windows += 1
            continue
        if event is None:
            continue
        try:
            windows.append(
                window_from_gamma_event(
                    event,
                    kind=kind,
                    start_time_utc=start_time,
                    end_time_utc=end_time,
                    slug=slug,
                )
            )
        except ValueError:
            skipped_windows += 1
    if not windows:
        return CachedUpDownBacktestResult(
            (),
            (),
            summarize_updown_entries([], initial_bankroll_usd=initial_bankroll_usd),
            skipped_windows=skipped_windows,
        )

    start = min(window.start_time_utc for window in windows)
    end = max(window.end_time_utc for window in windows)
    try:
        candles = _cached_candles(root / "candles" / f"coinbase_{int(start.timestamp())}_{int(end.timestamp())}.json", start, end, fetch_candles)
    except (requests.RequestException, ValueError, TypeError, OSError):
        return CachedUpDownBacktestResult(
            tuple(windows),
            (),
            summarize_updown_entries([], initial_bankroll_usd=initial_bankroll_usd),
            skipped_windows=skipped_windows + len(windows),
        )

    entries: list[UpDownBacktestEntry] = []
    for window in windows:
        try:
            resolution = resolve_updown_window(window, candles)
        except ValueError:
            skipped_windows += 1
            continue
        if data_source == "price_history":
            try:
                price_points = _load_window_price_history(root, window, fetch_price_history)
            except (requests.RequestException, ValueError, TypeError, OSError):
                skipped_windows += 1
                continue
            if not price_points:
                continue
            entries.extend(
                simulate_updown_price_entries(
                    window=window,
                    price_points=price_points,
                    resolution=resolution,
                    size_usd=size_usd,
                    policies=policies,
                )
            )
            continue
        try:
            raw_trades = _cached_json(
                root / "trades" / f"{window.condition_id}.json",
                lambda condition_id=window.condition_id: fetch_trades(condition_id),
            )
        except (requests.RequestException, ValueError, TypeError, OSError):
            skipped_windows += 1
            continue
        trades = parse_updown_trades(raw_trades or [], condition_id=window.condition_id)
        if not trades:
            continue
        entries.extend(
            simulate_updown_entries(
                window=window,
                trades=trades,
                resolution=resolution,
                size_usd=size_usd,
                policies=policies,
            )
        )
    return CachedUpDownBacktestResult(
        windows=tuple(windows),
        entries=tuple(entries),
        metrics=summarize_updown_entries(entries, initial_bankroll_usd=initial_bankroll_usd),
        skipped_windows=skipped_windows,
    )


def fetch_clob_price_history(
    *,
    token_id: str,
    start_time_utc: datetime,
    end_time_utc: datetime,
    fidelity_minutes: int = 1,
    timeout_seconds: int = 20,
) -> Mapping[str, object]:
    """Fetch public CLOB price history for one outcome token in read-only mode."""
    response = requests.get(
        "https://clob.polymarket.com/prices-history",
        params={
            "market": token_id,
            "startTs": int(_coerce_utc(start_time_utc).timestamp()),
            "endTs": int(_coerce_utc(end_time_utc).timestamp()),
            "fidelity": fidelity_minutes,
        },
        headers={"User-Agent": "btc-pm-research"},
        timeout=timeout_seconds,
    )
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, Mapping):
        raise ValueError("CLOB price history response must be an object")
    return payload


def fetch_gamma_event_by_slug(slug: str, *, timeout_seconds: int = 20) -> Mapping[str, object] | None:
    """Fetch one Gamma event by slug in read-only mode."""
    response = requests.get(
        "https://gamma-api.polymarket.com/events",
        params={"slug": slug},
        timeout=timeout_seconds,
    )
    response.raise_for_status()
    events = response.json()
    if not events:
        return None
    if not isinstance(events, list) or not isinstance(events[0], Mapping):
        raise ValueError("Gamma event response must be a list of objects")
    return events[0]


def fetch_data_api_trades(
    condition_id: str,
    *,
    limit: int = 1000,
    timeout_seconds: int = 20,
) -> list[Mapping[str, object]]:
    """Fetch Data API trades for one condition id in read-only mode."""
    response = requests.get(
        "https://data-api.polymarket.com/trades",
        params={"market": condition_id, "limit": limit, "takerOnly": "true"},
        timeout=timeout_seconds,
    )
    response.raise_for_status()
    trades = response.json()
    if not isinstance(trades, list):
        raise ValueError("Data API trades response must be a list")
    return trades


def fetch_coinbase_candles(
    *,
    start_time_utc: datetime,
    end_time_utc: datetime,
    timeout_seconds: int = 20,
) -> list[BTCCandle]:
    """Fetch Coinbase BTC/USD one-minute candles in read-only mode."""
    response = requests.get(
        "https://api.exchange.coinbase.com/products/BTC-USD/candles",
        params={
            "granularity": 60,
            "start": _iso_z(start_time_utc),
            "end": _iso_z(end_time_utc),
        },
        headers={"User-Agent": "btc-pm-research"},
        timeout=timeout_seconds,
    )
    response.raise_for_status()
    return parse_coinbase_candles(response.json())


def _cached_json(path: Path, fetcher: Callable[[], object]) -> object:
    """Read JSON from cache or fetch and write it."""
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    payload = fetcher()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True, separators=(",", ":")), encoding="utf-8")
    return payload


def _cached_candles(
    path: Path,
    start_time_utc: datetime,
    end_time_utc: datetime,
    fetcher: CandleFetcher,
) -> list[BTCCandle]:
    """Read candles from cache or fetch and write them."""
    if path.exists():
        rows = json.loads(path.read_text(encoding="utf-8"))
        return [
            BTCCandle(
                timestamp_utc=datetime.fromisoformat(str(row["timestamp_utc"])),
                open=float(row["open"]),
                close=float(row["close"]),
            )
            for row in rows
        ]
    candles = fetcher(start_time_utc, end_time_utc)
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        {
            "timestamp_utc": candle.timestamp_utc.isoformat(),
            "open": candle.open,
            "close": candle.close,
        }
        for candle in candles
    ]
    path.write_text(json.dumps(rows, sort_keys=True, separators=(",", ":")), encoding="utf-8")
    return candles


def _load_window_price_history(
    root: Path,
    window: UpDownWindow,
    fetcher: PriceHistoryFetcher,
) -> list[UpDownPricePoint]:
    """Load cached CLOB price history for all outcome tokens in one window."""
    if not window.outcome_token_ids:
        raise ValueError(f"{window.slug} missing outcome token ids")
    points: list[UpDownPricePoint] = []
    for outcome, token_id in window.outcome_token_ids:
        raw_history = _cached_json(
            root / "prices" / f"{token_id}_{int(window.start_time_utc.timestamp())}_{int(window.end_time_utc.timestamp())}.json",
            lambda token_id=token_id: fetcher(token_id, window.start_time_utc, window.end_time_utc),
        )
        if not isinstance(raw_history, Mapping):
            raise ValueError("cached CLOB price history must be an object")
        points.extend(parse_price_history(raw_history, outcome=outcome))
    return sorted(points, key=lambda point: point.timestamp_utc)


def _slug_spec(kind: str, start_ts: int, end_ts: int) -> tuple[str, datetime, datetime, str]:
    """Return one Up/Down slug spec."""
    return (
        kind,
        datetime.fromtimestamp(start_ts, timezone.utc),
        datetime.fromtimestamp(end_ts, timezone.utc),
        f"btc-updown-{kind}-{start_ts}",
    )


def _coerce_utc(value: datetime) -> datetime:
    """Return an aware UTC datetime."""
    if value.tzinfo is None:
        raise ValueError("datetime values must be timezone-aware")
    return value.astimezone(timezone.utc)


def _iso_z(value: datetime) -> str:
    """Format an aware UTC datetime for HTTP APIs."""
    return _coerce_utc(value).isoformat().replace("+00:00", "Z")


def _extract_outcome_token_ids(market: Mapping[str, object]) -> tuple[tuple[str, str], ...]:
    """Extract outcome-to-CLOB-token mapping from a Gamma market row."""
    outcomes = _coerce_string_list(market.get("outcomes"))
    token_ids = _coerce_string_list(market.get("clobTokenIds"))
    if len(outcomes) != len(token_ids):
        return ()
    return tuple((outcome, token_id) for outcome, token_id in zip(outcomes, token_ids) if outcome and token_id)


def _coerce_string_list(value: object) -> list[str]:
    """Coerce Gamma string-or-list JSON fields to a list of strings."""
    parsed = value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return []
    if not isinstance(parsed, list):
        return []
    return [str(item).strip() for item in parsed]


def _validate_updown_policies(policies: tuple[str, ...]) -> None:
    """Validate requested Up/Down entry policies."""
    if not policies:
        raise ValueError("at least one Up/Down entry policy is required")
    unknown = sorted(set(policies) - set(UPDOWN_ENTRY_POLICIES))
    if unknown:
        raise ValueError(f"unknown Up/Down entry policy: {', '.join(unknown)}")


def _validate_updown_data_source(data_source: str) -> None:
    """Validate requested Up/Down market data source."""
    if data_source not in UPDOWN_DATA_SOURCES:
        raise ValueError("data_source must be trades or price_history")
