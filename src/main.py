"""Command-line entry point for the BTC Polymarket research system."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Iterable, Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import TextIO

import numpy as np
import pandas as pd

from src.backtest import (
    calculate_binary_trade_pnl,
    generate_weekly_touch_markets,
    resolve_touch_market,
    run_cached_updown_backtest,
    summarize_updown_entries_by_group,
    summarize_backtest_metrics,
)
from src.data.btc_price_loader import BTCPriceLoader
from src.models import (
    ModelProbability,
    combine_model_probabilities,
    estimate_historical_volatility,
    run_bootstrap_fat_tail_model,
    run_monte_carlo_gbm,
)
from src.polymarket.gamma_client import GammaClient, GammaClientError
from src.polymarket.market_scanner import (
    DEFAULT_BTC_KEYWORDS,
    filter_tradeable_markets,
    search_btc_markets,
    standardize_market,
    standardize_markets,
)
from src.parser import parse_market_question
from src.paper import append_journal_entry, execute_paper_decision, read_journal
from src.reports import DailyReport, DailyReportMarket, write_daily_report
from src.strategy import TradeDecision


def scan_btc_tradeable_markets(
    *,
    client: GammaClient | None = None,
    keywords: Iterable[str] = DEFAULT_BTC_KEYWORDS,
    limit: int = 100,
    min_liquidity: float = 0.0,
) -> list[dict[str, object]]:
    """Run the read-only BTC market scan pipeline."""
    if limit <= 0:
        raise ValueError("limit must be positive")
    raw_markets = search_btc_markets(client, keywords=keywords, active=True, limit=limit)
    standardized = standardize_markets(raw_markets)
    return filter_tradeable_markets(standardized, min_liquidity=min_liquidity)


def main(
    argv: Sequence[str] | None = None,
    *,
    out: TextIO | None = None,
    client: GammaClient | None = None,
    price_data: pd.DataFrame | None = None,
) -> int:
    """Run the command-line interface."""
    output = out or sys.stdout
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command == "scan":
        return _run_scan(args, output=output, client=client)
    if args.command == "model":
        return _run_model(args, output=output, client=client, price_data=price_data)
    if args.command == "report":
        return _run_report(args, output=output)
    if args.command == "paper":
        return _run_paper(args, output=output)
    if args.command == "backtest":
        return _run_backtest(args, output=output)
    if args.command == "updown-backtest":
        return _run_updown_backtest(args, output=output)
    if args.command == "explain":
        return _run_explain(args, output=output, client=client)
    parser.print_help(file=output)
    return 0


def _build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    parser = argparse.ArgumentParser(prog="python -m src.main")
    subparsers = parser.add_subparsers(dest="command")
    scan_parser = subparsers.add_parser("scan", help="Scan BTC Polymarket markets in read-only mode")
    scan_parser.add_argument("--limit", type=int, default=100, help="Maximum Gamma markets to request")
    scan_parser.add_argument("--min-liquidity", type=float, default=0.0, help="Minimum market liquidity")
    scan_parser.add_argument(
        "--keyword",
        action="append",
        dest="keywords",
        help="BTC search keyword; may be provided more than once",
    )
    model_parser = subparsers.add_parser("model", help="Model a BTC Polymarket market in read-only mode")
    model_parser.add_argument("--market-id", required=True, help="Gamma market identifier")
    model_parser.add_argument("--price-period", default="1y", help="BTC price history period")
    model_parser.add_argument("--price-interval", default="1d", help="BTC price history interval")
    model_parser.add_argument("--vol-window", type=int, default=30, help="Historical volatility return window")
    model_parser.add_argument("--n-paths", type=int, default=5000, help="Simulation path count")
    model_parser.add_argument("--seed", type=int, default=42, help="Deterministic simulation seed")
    report_parser = subparsers.add_parser("report", help="Generate a local paper-trading Markdown report")
    report_parser.add_argument("--journal", default="data/paper/journal.jsonl", help="Paper journal JSONL path")
    report_parser.add_argument("--output", default="reports/daily_report.md", help="Markdown report output path")
    report_parser.add_argument("--spot-price-usd", type=float, default=None, help="Optional BTC spot price for the report")
    paper_parser = subparsers.add_parser("paper", help="Append a paper-only decision to the local journal")
    paper_parser.add_argument("--journal", default="data/paper/journal.jsonl", help="Paper journal JSONL path")
    paper_parser.add_argument("--market-id", required=True, help="Market identifier")
    paper_parser.add_argument("--question", required=True, help="Market question")
    paper_parser.add_argument("--action", required=True, choices=("BUY_YES", "BUY_NO", "HOLD"), help="Paper action")
    paper_parser.add_argument("--entry-price", type=float, default=None, help="Paper entry price for BUY actions")
    paper_parser.add_argument("--model-probability", type=float, required=True, help="Model probability")
    paper_parser.add_argument("--edge", type=float, default=0.0, help="Paper edge")
    paper_parser.add_argument("--expected-value", type=float, default=0.0, help="Paper expected value")
    paper_parser.add_argument("--size-usd", type=float, default=0.0, help="Paper size in USD")
    paper_parser.add_argument("--confidence", type=float, default=1.0, help="Decision confidence")
    backtest_parser = subparsers.add_parser("backtest", help="Run an offline synthetic BTC paper backtest")
    backtest_parser.add_argument("--rows", type=int, default=20, help="Synthetic daily price rows")
    backtest_parser.add_argument("--bankroll-usd", type=float, default=1000.0, help="Initial paper bankroll")
    backtest_parser.add_argument("--size-usd", type=float, default=10.0, help="Paper size per synthetic trade")
    updown_parser = subparsers.add_parser(
        "updown-backtest",
        help="Run a cached read-only BTC Up/Down paper backtest",
    )
    updown_parser.add_argument("--cache-dir", default="data/updown_cache", help="Local cache directory")
    updown_parser.add_argument("--lookback-minutes", type=int, default=180, help="Recent minutes to scan")
    updown_parser.add_argument("--bankroll-usd", type=float, default=1000.0, help="Initial paper bankroll")
    updown_parser.add_argument("--size-usd", type=float, default=10.0, help="Paper size per entry")
    updown_parser.add_argument("--no-15m", action="store_true", help="Exclude 15-minute Up/Down markets")
    updown_parser.add_argument(
        "--data-source",
        choices=("trades", "price_history"),
        default="trades",
        help="Historical market data source for simulated entries",
    )
    updown_parser.add_argument(
        "--policy",
        action="append",
        choices=("first_seen", "first_start_window", "last_before_end"),
        dest="policies",
        help="Entry policy to include; may be repeated",
    )
    explain_parser = subparsers.add_parser("explain", help="Explain parsed fields for one BTC market")
    explain_parser.add_argument("--market-id", required=True, help="Gamma market identifier")
    return parser


def _run_scan(args: argparse.Namespace, *, output: TextIO, client: GammaClient | None) -> int:
    """Run the scan subcommand."""
    keywords = tuple(args.keywords) if args.keywords else DEFAULT_BTC_KEYWORDS
    try:
        markets = scan_btc_tradeable_markets(
            client=client,
            keywords=keywords,
            limit=args.limit,
            min_liquidity=args.min_liquidity,
        )
    except (GammaClientError, ValueError, TypeError) as exc:
        print(f"scan failed: {exc}", file=output)
        return 1
    print("BTC Polymarket scan (read-only, paper-only)", file=output)
    if not markets:
        print("No tradeable BTC markets found.", file=output)
        return 0
    print("| market_id | question | yes_price | no_price | liquidity |", file=output)
    print("| --- | --- | ---: | ---: | ---: |", file=output)
    for market in markets:
        print(
            f"| {market.get('market_id')} | {market.get('question')} | "
            f"{_fmt_optional_float(market.get('yes_price'))} | "
            f"{_fmt_optional_float(market.get('no_price'))} | "
            f"{_fmt_optional_float(market.get('liquidity'))} |",
            file=output,
        )
    return 0


def _fmt_optional_float(value: object) -> str:
    """Format optional numeric CLI table values."""
    if value is None:
        return "n/a"
    return f"{float(value):.4f}"


def _run_model(
    args: argparse.Namespace,
    *,
    output: TextIO,
    client: GammaClient | None,
    price_data: pd.DataFrame | None,
) -> int:
    """Run the model subcommand."""
    try:
        result = model_market_probability(
            market_id=args.market_id,
            client=client,
            price_data=price_data,
            price_period=args.price_period,
            price_interval=args.price_interval,
            volatility_window=args.vol_window,
            n_paths=args.n_paths,
            random_seed=args.seed,
        )
    except (GammaClientError, ValueError, TypeError) as exc:
        print(f"model failed: {exc}", file=output)
        return 1

    print("BTC Polymarket model (read-only, paper-only)", file=output)
    print(f"market_id: {result['market_id']}", file=output)
    print(f"question: {result['question']}", file=output)
    print(f"event_type: {result['event_type']}", file=output)
    print(f"target_price_usd: {_fmt_optional_float(result['target_price'])}", file=output)
    print(f"current_price_usd: {_fmt_optional_float(result['current_price'])}", file=output)
    print(f"days_to_expiry: {_fmt_optional_float(result['days_to_expiry'])}", file=output)
    print(f"annualized_volatility: {_fmt_optional_float(result['annualized_volatility'])}", file=output)
    print(f"monte_carlo_probability: {_fmt_optional_float(result['monte_carlo_probability'])}", file=output)
    print(f"bootstrap_probability: {_fmt_optional_float(result['bootstrap_probability'])}", file=output)
    print(f"ensemble_probability: {_fmt_optional_float(result['ensemble_probability'])}", file=output)
    warnings = result["warnings"]
    if warnings:
        print(f"warnings: {', '.join(warnings)}", file=output)
    return 0


def model_market_probability(
    *,
    market_id: str,
    client: GammaClient | None = None,
    price_data: pd.DataFrame | None = None,
    price_period: str = "1y",
    price_interval: str = "1d",
    volatility_window: int = 30,
    n_paths: int = 5000,
    random_seed: int = 42,
) -> dict[str, object]:
    """Fetch one market and estimate a read-only model probability."""
    clean_market_id = str(market_id).strip()
    if not clean_market_id:
        raise ValueError("market_id is required")
    gamma_client = client or GammaClient()
    market = standardize_market(gamma_client.get_market(clean_market_id))
    question = str(market.get("question") or "").strip()
    parsed = parse_market_question(question)
    if parsed.target_price is None:
        raise ValueError("market target price could not be parsed")
    if parsed.deadline_utc is None:
        raise ValueError("market deadline could not be parsed")
    if parsed.event_type not in {"touch", "terminal"}:
        raise ValueError("market event type could not be parsed")

    prices = price_data if price_data is not None else BTCPriceLoader().load_history(period=price_period, interval=price_interval)
    volatility = estimate_historical_volatility(prices, window=volatility_window)
    days_to_expiry = (parsed.deadline_utc - volatility.as_of_utc.astimezone(timezone.utc)).total_seconds() / 86400.0
    if days_to_expiry <= 0:
        raise ValueError("market deadline must be after the BTC price data timestamp")
    current_price = volatility.latest_close
    returns = _historical_log_returns(prices)

    mode = parsed.event_type
    monte_carlo = run_monte_carlo_gbm(
        current_price=current_price,
        target_price=parsed.target_price,
        days_to_expiry=days_to_expiry,
        annualized_volatility=volatility.annualized_volatility,
        drift=volatility.annualized_mean_log_return,
        n_paths=n_paths,
        random_seed=random_seed,
        mode=mode,
    )
    bootstrap = run_bootstrap_fat_tail_model(
        current_price=current_price,
        target_price=parsed.target_price,
        historical_log_returns=returns,
        days_to_expiry=days_to_expiry,
        n_paths=n_paths,
        random_seed=random_seed,
        mode=mode,
    )
    ensemble = combine_model_probabilities(
        (
            ModelProbability("monte_carlo", monte_carlo.probability),
            ModelProbability("bootstrap", bootstrap.probability),
        )
    )
    return {
        "market_id": market.get("market_id"),
        "question": question,
        "event_type": parsed.event_type,
        "target_price": parsed.target_price,
        "current_price": current_price,
        "days_to_expiry": days_to_expiry,
        "annualized_volatility": volatility.annualized_volatility,
        "monte_carlo_probability": monte_carlo.probability,
        "bootstrap_probability": bootstrap.probability,
        "ensemble_probability": ensemble.probability,
        "warnings": tuple(parsed.warnings + volatility.warnings + ensemble.warnings),
    }


def _historical_log_returns(price_data: pd.DataFrame) -> list[float]:
    """Return historical close-to-close log returns for bootstrap modeling."""
    closes = pd.to_numeric(price_data["close"], errors="coerce")
    returns = np.log(closes / closes.shift(1)).dropna()
    return [float(value) for value in returns if np.isfinite(value)]


def _run_report(args: argparse.Namespace, *, output: TextIO) -> int:
    """Run the report subcommand."""
    try:
        report = build_daily_report_from_journal(
            journal_path=args.journal,
            generated_at_utc=datetime.now(timezone.utc),
            spot_price_usd=args.spot_price_usd,
        )
        write_daily_report(args.output, report)
    except (ValueError, OSError, TypeError) as exc:
        print(f"report failed: {exc}", file=output)
        return 1
    print(f"wrote paper-only report: {args.output}", file=output)
    return 0


def build_daily_report_from_journal(
    *,
    journal_path: str | Path,
    generated_at_utc: datetime,
    spot_price_usd: float | None = None,
) -> DailyReport:
    """Build a daily report from the local paper journal."""
    rows = read_journal(journal_path)
    markets = tuple(_journal_row_to_report_market(row) for row in rows)
    btc_state: dict[str, object] = {}
    if spot_price_usd is not None:
        if spot_price_usd <= 0:
            raise ValueError("spot_price_usd must be positive")
        btc_state["spot_price_usd"] = f"${spot_price_usd:,.2f} USD"
    best = _best_opportunity(markets)
    return DailyReport(
        generated_at_utc=generated_at_utc,
        btc_current_state=btc_state,
        markets=markets,
        best_opportunity=best,
        largest_risk="Paper results depend on model uncertainty, liquidity, and manually supplied prices.",
        model_uncertainty="Report uses saved paper records only; it does not fetch live probabilities.",
    )


def _journal_row_to_report_market(row: dict[str, object]) -> DailyReportMarket:
    """Convert one paper journal row to a daily report market row."""
    side = str(row.get("side", "NONE"))
    entry_price = row.get("entry_price")
    yes_price = float(entry_price) if side == "YES" and entry_price is not None else None
    no_price = float(entry_price) if side == "NO" and entry_price is not None else None
    rationale = row.get("rationale", [])
    reasons = tuple(str(item) for item in rationale) if isinstance(rationale, list) else ()
    return DailyReportMarket(
        market_id=str(row.get("market_id", "")),
        question=str(row.get("question", "")),
        yes_price=yes_price,
        no_price=no_price,
        model_probability=float(row.get("model_probability", 0.0)),
        edge=float(row.get("edge", 0.0)),
        action=str(row.get("action", "HOLD")),
        suggested_limit_price=float(entry_price) if entry_price is not None else None,
        suggested_position_usd=float(row.get("size_usd", 0.0)),
        reasons_not_to_trade=reasons,
        model_uncertainty="from saved paper journal",
    )


def _best_opportunity(markets: tuple[DailyReportMarket, ...]) -> str:
    """Select a simple best-opportunity label for the report."""
    actionable = [market for market in markets if market.action != "HOLD"]
    if not actionable:
        return "No paper opportunity selected."
    selected = max(actionable, key=lambda market: abs(market.edge or 0.0))
    return f"{selected.market_id}: {selected.action} with edge {_fmt_optional_float(selected.edge)}"


def _run_paper(args: argparse.Namespace, *, output: TextIO) -> int:
    """Run the paper subcommand."""
    try:
        decision = TradeDecision(
            action=args.action,
            model_probability=args.model_probability,
            market_price=args.entry_price,
            edge=args.edge,
            expected_value=args.expected_value,
            suggested_limit_price=args.entry_price,
            position_size_usd=args.size_usd,
            max_loss_usd=args.size_usd,
            confidence=args.confidence,
            reasons=("cli_paper_entry",),
        )
        execution = execute_paper_decision(
            decision=decision,
            market_id=args.market_id,
            question=args.question,
        )
        append_journal_entry(args.journal, execution)
    except (ValueError, OSError, TypeError) as exc:
        print(f"paper failed: {exc}", file=output)
        return 1
    print(f"appended paper-only {execution.action} for {execution.market_id} to {args.journal}", file=output)
    return 0


def _run_backtest(args: argparse.Namespace, *, output: TextIO) -> int:
    """Run the backtest subcommand."""
    try:
        metrics = run_synthetic_backtest(
            rows=args.rows,
            initial_bankroll_usd=args.bankroll_usd,
            size_usd=args.size_usd,
        )
    except (ValueError, TypeError) as exc:
        print(f"backtest failed: {exc}", file=output)
        return 1
    print("BTC synthetic backtest (offline, paper-only)", file=output)
    print(f"number_of_trades: {metrics.number_of_trades}", file=output)
    print(f"total_return: {_fmt_optional_float(metrics.total_return)}", file=output)
    print(f"win_rate: {_fmt_optional_float(metrics.win_rate)}", file=output)
    print(f"max_drawdown: {_fmt_optional_float(metrics.max_drawdown)}", file=output)
    print(f"exposure: {_fmt_optional_float(metrics.exposure)}", file=output)
    return 0


def _run_updown_backtest(args: argparse.Namespace, *, output: TextIO) -> int:
    """Run the cached BTC Up/Down backtest subcommand."""
    try:
        result = run_cached_updown_backtest(
            cache_dir=args.cache_dir,
            now_utc=datetime.now(timezone.utc),
            lookback_minutes=args.lookback_minutes,
            include_15m=not args.no_15m,
            size_usd=args.size_usd,
            initial_bankroll_usd=args.bankroll_usd,
            policies=(
                tuple(args.policies)
                if args.policies
                else ("first_seen", "first_start_window", "last_before_end")
            ),
            data_source=args.data_source,
        )
    except (ValueError, TypeError, OSError) as exc:
        print(f"updown-backtest failed: {exc}", file=output)
        return 1
    metrics = result.metrics
    print("BTC Up/Down cached backtest (read-only, paper-only)", file=output)
    print(f"data_source: {args.data_source}", file=output)
    print(f"windows: {len(result.windows)}", file=output)
    print(f"skipped_windows: {result.skipped_windows}", file=output)
    print(f"entries: {len(result.entries)}", file=output)
    print(f"number_of_trades: {metrics.number_of_trades}", file=output)
    print(f"total_return: {_fmt_optional_float(metrics.total_return)}", file=output)
    print(f"win_rate: {_fmt_optional_float(metrics.win_rate)}", file=output)
    print(f"max_drawdown: {_fmt_optional_float(metrics.max_drawdown)}", file=output)
    print(f"exposure: {_fmt_optional_float(metrics.exposure)}", file=output)
    _print_updown_group_metrics("by_policy", summarize_updown_entries_by_group(result.entries, group_by="policy", initial_bankroll_usd=args.bankroll_usd), output)
    _print_updown_group_metrics("by_kind", summarize_updown_entries_by_group(result.entries, group_by="kind", initial_bankroll_usd=args.bankroll_usd), output)
    return 0


def _print_updown_group_metrics(label: str, groups: dict[str, object], output: TextIO) -> None:
    """Print compact grouped Up/Down metrics."""
    if not groups:
        return
    print(label + ":", file=output)
    for key, metrics in groups.items():
        print(
            f"  {key}: trades={metrics.number_of_trades} "
            f"total_return={_fmt_optional_float(metrics.total_return)} "
            f"win_rate={_fmt_optional_float(metrics.win_rate)} "
            f"max_drawdown={_fmt_optional_float(metrics.max_drawdown)}",
            file=output,
        )


def run_synthetic_backtest(*, rows: int = 20, initial_bankroll_usd: float = 1000.0, size_usd: float = 10.0):
    """Run a deterministic synthetic weekly touch-market paper backtest."""
    if rows < 8:
        raise ValueError("rows must be at least 8")
    if size_usd < 0:
        raise ValueError("size_usd must be non-negative")
    price_data = _synthetic_price_data(rows)
    markets = generate_weekly_touch_markets(price_data.iloc[:-7])
    pnls: list[float] = []
    exposures: list[float] = []
    for market in markets:
        resolution = resolve_touch_market(price_data, market=market)
        pnls.append(
            calculate_binary_trade_pnl(
                side="BUY_YES",
                entry_price=0.50,
                size_usd=size_usd,
                resolved_yes=resolution.touched,
            )
        )
        exposures.append(size_usd)
    return summarize_backtest_metrics(pnls, initial_bankroll_usd=initial_bankroll_usd, exposures_usd=exposures)


def _synthetic_price_data(rows: int) -> pd.DataFrame:
    """Create deterministic OHLCV data for the CLI synthetic backtest."""
    dates = pd.date_range("2026-01-01", periods=rows, freq="D", tz="UTC")
    close = [100.0 + index for index in range(rows)]
    return pd.DataFrame(
        {
            "timestamp_utc": dates,
            "open": close,
            "high": [value * 1.06 for value in close],
            "low": [value * 0.96 for value in close],
            "close": close,
            "volume": [1.0 for _ in close],
        }
    )


def _run_explain(args: argparse.Namespace, *, output: TextIO, client: GammaClient | None) -> int:
    """Run the explain subcommand."""
    try:
        explanation = explain_market(args.market_id, client=client)
    except (GammaClientError, ValueError, TypeError) as exc:
        print(f"explain failed: {exc}", file=output)
        return 1
    print("BTC Polymarket explain (read-only, paper-only)", file=output)
    for key in ("market_id", "question", "asset", "target_price", "direction", "event_type", "deadline_utc", "confidence"):
        print(f"{key}: {explanation[key]}", file=output)
    warnings = explanation["warnings"]
    if warnings:
        print(f"warnings: {', '.join(warnings)}", file=output)
    return 0


def explain_market(market_id: str, *, client: GammaClient | None = None) -> dict[str, object]:
    """Fetch one market and explain its parsed question fields."""
    clean_market_id = str(market_id).strip()
    if not clean_market_id:
        raise ValueError("market_id is required")
    gamma_client = client or GammaClient()
    market = standardize_market(gamma_client.get_market(clean_market_id))
    question = str(market.get("question") or "").strip()
    parsed = parse_market_question(question)
    return {
        "market_id": market.get("market_id"),
        "question": question,
        "asset": parsed.asset,
        "target_price": parsed.target_price,
        "direction": parsed.direction,
        "event_type": parsed.event_type,
        "deadline_utc": parsed.deadline_utc.isoformat() if parsed.deadline_utc else None,
        "confidence": parsed.confidence,
        "warnings": parsed.warnings,
    }


if __name__ == "__main__":
    raise SystemExit(main())
