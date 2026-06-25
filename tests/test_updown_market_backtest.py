import io
import unittest
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import requests

from src.main import main
from src.backtest import (
    BTCCandle,
    BacktestMetrics,
    CachedUpDownBacktestResult,
    UpDownBacktestEntry,
    UpDownWindow,
    build_recent_updown_slugs,
    parse_coinbase_candles,
    parse_updown_trades,
    resolve_updown_window,
    run_cached_updown_backtest,
    simulate_updown_entries,
    summarize_updown_entries,
    summarize_updown_entries_by_group,
    window_from_gamma_event,
)


class UpDownMarketBacktestTests(unittest.TestCase):
    def test_build_recent_updown_slugs_generates_completed_windows(self) -> None:
        now = datetime.fromtimestamp(1782285900, timezone.utc)

        specs = build_recent_updown_slugs(now_utc=now, lookback_minutes=30)

        slugs = [spec[3] for spec in specs]
        self.assertIn("btc-updown-5m-1782285300", slugs)
        self.assertIn("btc-updown-15m-1782284400", slugs)
        for _kind, _start, end, _slug in specs:
            self.assertLess(end, now)

    def test_parse_resolve_simulate_and_summarize_updown_entries(self) -> None:
        start = datetime.fromtimestamp(1782285000, timezone.utc)
        end = datetime.fromtimestamp(1782285300, timezone.utc)
        event = {"markets": [{"conditionId": "0xabc"}]}
        window = window_from_gamma_event(
            event,
            kind="5m",
            start_time_utc=start,
            end_time_utc=end,
            slug="btc-updown-5m-1782285000",
        )
        trades = parse_updown_trades(
            (
                {
                    "timestamp": 1782285010,
                    "outcome": "Up",
                    "side": "BUY",
                    "price": 0.40,
                    "size": 12.0,
                },
                {
                    "timestamp": 1782285020,
                    "outcome": "Down",
                    "side": "BUY",
                    "price": 0.55,
                    "size": 8.0,
                },
                {
                    "timestamp": 1782285200,
                    "outcome": "Up",
                    "side": "BUY",
                    "price": 0.75,
                    "size": 4.0,
                },
            ),
            condition_id=window.condition_id,
        )
        candles = parse_coinbase_candles(
            (
                [1782285000, 99.0, 101.0, 100.0, 100.2, 1.0],
                [1782285300, 100.1, 102.0, 100.2, 101.0, 1.0],
            )
        )

        resolution = resolve_updown_window(window, candles)
        entries = simulate_updown_entries(window=window, trades=trades, resolution=resolution, size_usd=10.0)
        summary = summarize_updown_entries(entries, initial_bankroll_usd=1000.0)

        self.assertEqual(resolution.winner, "Up")
        self.assertEqual(len(entries), 6)
        self.assertTrue(any(entry.policy == "first_start_window" for entry in entries))
        self.assertTrue(any(entry.outcome == "Up" and entry.pnl_usd > 0.0 for entry in entries))
        self.assertTrue(any(entry.outcome == "Down" and entry.pnl_usd < 0.0 for entry in entries))
        self.assertEqual(summary.number_of_trades, len(entries))
        self.assertGreater(summary.exposure, 0.0)
        by_policy = summarize_updown_entries_by_group(entries, group_by="policy", initial_bankroll_usd=1000.0)
        by_kind = summarize_updown_entries_by_group(entries, group_by="kind", initial_bankroll_usd=1000.0)
        self.assertIn("first_seen", by_policy)
        self.assertEqual(by_kind["5m"].number_of_trades, len(entries))

    def test_window_from_gamma_event_rejects_missing_condition_id(self) -> None:
        with self.assertRaises(ValueError):
            window_from_gamma_event(
                {"markets": [{}]},
                kind="5m",
                start_time_utc=datetime.fromtimestamp(1782285000, timezone.utc),
                end_time_utc=datetime.fromtimestamp(1782285300, timezone.utc),
                slug="btc-updown-5m-1782285000",
            )

    def test_run_cached_updown_backtest_reuses_cached_api_rows(self) -> None:
        now = datetime.fromtimestamp(1782285900, timezone.utc)
        calls = {"events": 0, "trades": 0, "candles": 0}

        def fake_event_fetcher(slug: str):
            calls["events"] += 1
            if slug == "btc-updown-5m-1782285300":
                return {"markets": [{"conditionId": "0xdef"}]}
            return None

        def fake_trades_fetcher(condition_id: str):
            calls["trades"] += 1
            self.assertEqual(condition_id, "0xdef")
            return [
                {
                    "timestamp": 1782285310,
                    "outcome": "Up",
                    "side": "BUY",
                    "price": 0.50,
                    "size": 10.0,
                },
                {
                    "timestamp": 1782285320,
                    "outcome": "Down",
                    "side": "BUY",
                    "price": 0.50,
                    "size": 10.0,
                },
            ]

        def fake_candle_fetcher(start_time_utc: datetime, end_time_utc: datetime):
            calls["candles"] += 1
            return [
                BTCCandle(timestamp_utc=start_time_utc, open=100.0, close=100.5),
                BTCCandle(timestamp_utc=end_time_utc, open=100.5, close=101.0),
            ]

        with TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            first = run_cached_updown_backtest(
                cache_dir=cache_dir,
                now_utc=now,
                lookback_minutes=10,
                include_15m=False,
                event_fetcher=fake_event_fetcher,
                trades_fetcher=fake_trades_fetcher,
                candle_fetcher=fake_candle_fetcher,
            )
            second = run_cached_updown_backtest(
                cache_dir=cache_dir,
                now_utc=now,
                lookback_minutes=10,
                include_15m=False,
                event_fetcher=lambda slug: self.fail(f"unexpected event fetch: {slug}"),
                trades_fetcher=lambda condition_id: self.fail(f"unexpected trade fetch: {condition_id}"),
                candle_fetcher=lambda start, end: self.fail("unexpected candle fetch"),
            )

        self.assertEqual(calls, {"events": 1, "trades": 1, "candles": 1})
        self.assertEqual(len(first.windows), 1)
        self.assertEqual(first.metrics.number_of_trades, second.metrics.number_of_trades)
        self.assertEqual(first.metrics.total_return, second.metrics.total_return)

    def test_run_cached_updown_backtest_skips_trade_fetch_failures(self) -> None:
        now = datetime.fromtimestamp(1782285900, timezone.utc)

        def fake_event_fetcher(slug: str):
            if slug == "btc-updown-5m-1782285300":
                return {"markets": [{"conditionId": "0xdef"}]}
            return None

        def failing_trades_fetcher(condition_id: str):
            raise requests.Timeout("slow public API")

        def fake_candle_fetcher(start_time_utc: datetime, end_time_utc: datetime):
            return [
                BTCCandle(timestamp_utc=start_time_utc, open=100.0, close=100.5),
                BTCCandle(timestamp_utc=end_time_utc, open=100.5, close=101.0),
            ]

        with TemporaryDirectory() as temp_dir:
            result = run_cached_updown_backtest(
                cache_dir=Path(temp_dir),
                now_utc=now,
                lookback_minutes=10,
                include_15m=False,
                event_fetcher=fake_event_fetcher,
                trades_fetcher=failing_trades_fetcher,
                candle_fetcher=fake_candle_fetcher,
            )

        self.assertEqual(len(result.windows), 1)
        self.assertEqual(result.entries, ())
        self.assertEqual(result.metrics.number_of_trades, 0)
        self.assertEqual(result.skipped_windows, 1)

    def test_run_cached_updown_backtest_filters_entry_policies(self) -> None:
        now = datetime.fromtimestamp(1782285900, timezone.utc)

        def fake_event_fetcher(slug: str):
            if slug == "btc-updown-5m-1782285300":
                return {"markets": [{"conditionId": "0xdef"}]}
            return None

        def fake_trades_fetcher(condition_id: str):
            return [
                {
                    "timestamp": 1782285310,
                    "outcome": "Up",
                    "side": "BUY",
                    "price": 0.50,
                    "size": 10.0,
                },
                {
                    "timestamp": 1782285320,
                    "outcome": "Down",
                    "side": "BUY",
                    "price": 0.50,
                    "size": 10.0,
                },
            ]

        def fake_candle_fetcher(start_time_utc: datetime, end_time_utc: datetime):
            return [
                BTCCandle(timestamp_utc=start_time_utc, open=100.0, close=100.5),
                BTCCandle(timestamp_utc=end_time_utc, open=100.5, close=101.0),
            ]

        with TemporaryDirectory() as temp_dir:
            result = run_cached_updown_backtest(
                cache_dir=Path(temp_dir),
                now_utc=now,
                lookback_minutes=10,
                include_15m=False,
                policies=("first_start_window",),
                event_fetcher=fake_event_fetcher,
                trades_fetcher=fake_trades_fetcher,
                candle_fetcher=fake_candle_fetcher,
            )

        self.assertEqual({entry.policy for entry in result.entries}, {"first_start_window"})
        self.assertEqual(result.metrics.number_of_trades, 2)

    def test_run_cached_updown_backtest_uses_price_history_source(self) -> None:
        now = datetime.fromtimestamp(1782285900, timezone.utc)

        def fake_event_fetcher(slug: str):
            if slug == "btc-updown-5m-1782285300":
                return {
                    "markets": [
                        {
                            "conditionId": "0xdef",
                            "outcomes": '["Up", "Down"]',
                            "clobTokenIds": '["up-token", "down-token"]',
                        }
                    ]
                }
            return None

        def fake_price_history_fetcher(token_id: str, start_time_utc: datetime, end_time_utc: datetime):
            if token_id == "up-token":
                return {"history": [{"t": 1782285310, "p": 0.45}, {"t": 1782285320, "p": 0.60}]}
            if token_id == "down-token":
                return {"history": [{"t": 1782285310, "p": 0.55}, {"t": 1782285320, "p": 0.40}]}
            self.fail(f"unexpected token_id: {token_id}")

        def fake_candle_fetcher(start_time_utc: datetime, end_time_utc: datetime):
            return [
                BTCCandle(timestamp_utc=start_time_utc, open=100.0, close=100.5),
                BTCCandle(timestamp_utc=end_time_utc, open=100.5, close=101.0),
            ]

        with TemporaryDirectory() as temp_dir:
            result = run_cached_updown_backtest(
                cache_dir=Path(temp_dir),
                now_utc=now,
                lookback_minutes=10,
                include_15m=False,
                policies=("first_seen",),
                data_source="price_history",
                event_fetcher=fake_event_fetcher,
                price_history_fetcher=fake_price_history_fetcher,
                candle_fetcher=fake_candle_fetcher,
            )

        self.assertEqual(len(result.windows), 1)
        self.assertEqual(result.metrics.number_of_trades, 2)
        self.assertEqual({entry.policy for entry in result.entries}, {"first_seen"})
        self.assertTrue(any(entry.outcome == "Up" and entry.pnl_usd > 0.0 for entry in result.entries))
        self.assertTrue(any(entry.outcome == "Down" and entry.pnl_usd < 0.0 for entry in result.entries))

    def test_main_updown_backtest_passes_selected_policy(self) -> None:
        output = io.StringIO()
        window = UpDownWindow(
            kind="5m",
            slug="btc-updown-5m-1782285000",
            condition_id="0xabc",
            start_time_utc=datetime.fromtimestamp(1782285000, timezone.utc),
            end_time_utc=datetime.fromtimestamp(1782285300, timezone.utc),
        )
        entry = UpDownBacktestEntry(
            slug=window.slug,
            kind=window.kind,
            policy="first_start_window",
            outcome="Up",
            winner="Up",
            entry_price=0.50,
            size_usd=10.0,
            pnl_usd=10.0,
            entry_time_utc=datetime.fromtimestamp(1782285010, timezone.utc),
        )
        fake_result = CachedUpDownBacktestResult(
            windows=(window,),
            entries=(entry,),
            metrics=BacktestMetrics(
                total_return=0.01,
                win_rate=1.0,
                average_win=10.0,
                average_loss=0.0,
                max_drawdown=0.0,
                profit_factor=0.0,
                roi_per_trade=0.01,
                largest_loss=0.0,
                losing_streak=0,
                number_of_trades=1,
                exposure=0.01,
            ),
        )

        with patch("src.main.run_cached_updown_backtest", return_value=fake_result) as runner:
            exit_code = main(
                [
                    "updown-backtest",
                    "--cache-dir",
                    "data/test_updown_cache",
                    "--lookback-minutes",
                    "30",
                    "--policy",
                    "first_start_window",
                    "--no-15m",
                ],
                out=output,
            )

        self.assertEqual(exit_code, 0)
        self.assertEqual(runner.call_args.kwargs["policies"], ("first_start_window",))
        self.assertIn("first_start_window: trades=1", output.getvalue())

    def test_main_updown_backtest_passes_price_history_source(self) -> None:
        output = io.StringIO()
        fake_result = CachedUpDownBacktestResult(
            windows=(),
            entries=(),
            metrics=BacktestMetrics(
                total_return=0.0,
                win_rate=0.0,
                average_win=0.0,
                average_loss=0.0,
                max_drawdown=0.0,
                profit_factor=0.0,
                roi_per_trade=0.0,
                largest_loss=0.0,
                losing_streak=0,
                number_of_trades=0,
                exposure=0.0,
            ),
        )

        with patch("src.main.run_cached_updown_backtest", return_value=fake_result) as runner:
            exit_code = main(
                [
                    "updown-backtest",
                    "--data-source",
                    "price_history",
                    "--policy",
                    "first_seen",
                ],
                out=output,
            )

        self.assertEqual(exit_code, 0)
        self.assertEqual(runner.call_args.kwargs["data_source"], "price_history")
        self.assertIn("data_source: price_history", output.getvalue())


if __name__ == "__main__":
    unittest.main()
