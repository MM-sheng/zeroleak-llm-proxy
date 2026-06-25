import unittest
from datetime import datetime, timezone

import pandas as pd

from src.backtest import (
    BacktestMetrics,
    SyntheticBTCMarket,
    TouchResolution,
    assert_no_future_data,
    calculate_binary_trade_pnl,
    estimate_prior_volatility,
    generate_synthetic_btc_markets,
    generate_weekly_touch_markets,
    resolve_touch_market,
    summarize_backtest_metrics,
)


class SyntheticMarketGeneratorTests(unittest.TestCase):
    def test_generate_synthetic_btc_markets_creates_markets_from_price_rows(self) -> None:
        price_data = pd.DataFrame(
            {
                "timestamp_utc": pd.to_datetime(["2026-01-01", "2026-01-02"], utc=True),
                "close": [100000.0, 110000.0],
            }
        )

        markets = generate_synthetic_btc_markets(
            price_data,
            target_multipliers=(1.05, 0.95),
            days_to_expiry=7,
            event_type="touch",
        )

        self.assertEqual(len(markets), 4)
        self.assertIsInstance(markets[0], SyntheticBTCMarket)
        self.assertTrue(markets[0].market_id.startswith("synthetic-btc-touch-"))
        self.assertEqual(markets[0].direction, "above")
        self.assertEqual(markets[1].direction, "below")
        self.assertEqual(markets[0].target_price, 105000.0)
        self.assertEqual(markets[0].decision_time_utc, datetime(2026, 1, 1, tzinfo=timezone.utc))
        self.assertEqual(markets[0].deadline_utc, datetime(2026, 1, 8, tzinfo=timezone.utc))
        self.assertIn("synthetic", markets[0].market_id)

    def test_generate_synthetic_btc_markets_supports_terminal_markets(self) -> None:
        price_data = pd.DataFrame(
            {
                "timestamp_utc": pd.to_datetime(["2026-01-01"], utc=True),
                "close": [100000.0],
            }
        )

        markets = generate_synthetic_btc_markets(price_data, target_multipliers=(1.10,), event_type="terminal")

        self.assertEqual(markets[0].event_type, "terminal")
        self.assertIn("close above", markets[0].question)

    def test_generate_weekly_touch_markets_uses_standard_targets(self) -> None:
        price_data = pd.DataFrame(
            {
                "timestamp_utc": pd.to_datetime(["2026-01-01"], utc=True),
                "close": [100000.0],
            }
        )

        markets = generate_weekly_touch_markets(price_data)

        self.assertEqual(len(markets), 3)
        self.assertEqual([market.event_type for market in markets], ["touch", "touch", "touch"])
        self.assertEqual([market.target_price for market in markets], [105000.0, 110000.0, 95000.0])
        self.assertEqual([market.direction for market in markets], ["above", "above", "below"])
        self.assertEqual(markets[0].deadline_utc, datetime(2026, 1, 8, tzinfo=timezone.utc))

    def test_generate_synthetic_btc_markets_rejects_invalid_inputs(self) -> None:
        valid = pd.DataFrame(
            {
                "timestamp_utc": pd.to_datetime(["2026-01-01"], utc=True),
                "close": [100000.0],
            }
        )
        invalid_cases = [
            (valid, {"days_to_expiry": 0}),
            (valid, {"event_type": "bad"}),
            (valid, {"target_multipliers": ()}),
            (valid, {"target_multipliers": (0.0,)}),
            (pd.DataFrame({"timestamp_utc": pd.to_datetime(["2026-01-01"], utc=True)}), {}),
        ]

        for frame, kwargs in invalid_cases:
            with self.subTest(kwargs=kwargs):
                with self.assertRaises((TypeError, ValueError)):
                    generate_synthetic_btc_markets(frame, **kwargs)


class PriorVolatilityBacktestTests(unittest.TestCase):
    def test_estimate_prior_volatility_uses_only_rows_before_decision_time(self) -> None:
        price_data = pd.DataFrame(
            {
                "timestamp_utc": pd.to_datetime(
                    ["2026-01-01", "2026-01-02", "2026-01-03", "2026-01-04"],
                    utc=True,
                ),
                "close": [100.0, 110.0, 121.0, 300.0],
            }
        )

        estimate = estimate_prior_volatility(
            price_data,
            decision_time_utc=datetime(2026, 1, 4, tzinfo=timezone.utc),
            window=2,
            periods_per_year=365,
        )

        self.assertEqual(estimate.as_of_utc, datetime(2026, 1, 3, tzinfo=timezone.utc))
        self.assertEqual(estimate.latest_close, 121.0)

    def test_estimate_prior_volatility_rejects_missing_prior_rows(self) -> None:
        price_data = pd.DataFrame(
            {
                "timestamp_utc": pd.to_datetime(["2026-01-01"], utc=True),
                "close": [100.0],
            }
        )

        with self.assertRaises(ValueError):
            estimate_prior_volatility(
                price_data,
                decision_time_utc=datetime(2026, 1, 1, tzinfo=timezone.utc),
                window=2,
            )


class NoFutureDataGuardTests(unittest.TestCase):
    def test_assert_no_future_data_accepts_prior_rows(self) -> None:
        data = pd.DataFrame(
            {
                "timestamp_utc": pd.to_datetime(["2026-01-01", "2026-01-02"], utc=True),
                "feature": [1.0, 2.0],
            }
        )

        result = assert_no_future_data(data, decision_time_utc=datetime(2026, 1, 3, tzinfo=timezone.utc))

        self.assertEqual(len(result), 2)

    def test_assert_no_future_data_rejects_current_or_future_rows(self) -> None:
        data = pd.DataFrame(
            {
                "timestamp_utc": pd.to_datetime(["2026-01-01", "2026-01-03"], utc=True),
                "feature": [1.0, 2.0],
            }
        )

        with self.assertRaises(ValueError):
            assert_no_future_data(data, decision_time_utc=datetime(2026, 1, 3, tzinfo=timezone.utc))

    def test_assert_no_future_data_rejects_invalid_inputs(self) -> None:
        with self.assertRaises(ValueError):
            assert_no_future_data(
                pd.DataFrame({"not_time": [1]}),
                decision_time_utc=datetime(2026, 1, 3, tzinfo=timezone.utc),
            )
        with self.assertRaises(ValueError):
            assert_no_future_data(
                pd.DataFrame({"timestamp_utc": ["bad"]}),
                decision_time_utc=datetime(2026, 1, 3, tzinfo=timezone.utc),
            )


class TouchMarketResolutionTests(unittest.TestCase):
    def test_resolve_touch_market_detects_above_touch_after_decision(self) -> None:
        market = SyntheticBTCMarket(
            market_id="synthetic-touch",
            question="Will BTC touch above?",
            event_type="touch",
            direction="above",
            target_price=105.0,
            decision_time_utc=datetime(2026, 1, 1, tzinfo=timezone.utc),
            deadline_utc=datetime(2026, 1, 4, tzinfo=timezone.utc),
            initial_price=100.0,
        )
        price_data = pd.DataFrame(
            {
                "timestamp_utc": pd.to_datetime(["2026-01-01", "2026-01-02", "2026-01-03"], utc=True),
                "high": [200.0, 104.0, 106.0],
                "low": [50.0, 99.0, 101.0],
            }
        )

        resolution = resolve_touch_market(price_data, market=market)

        self.assertIsInstance(resolution, TouchResolution)
        self.assertTrue(resolution.touched)
        self.assertEqual(resolution.touch_time_utc, datetime(2026, 1, 3, tzinfo=timezone.utc))
        self.assertEqual(resolution.max_price, 106.0)
        self.assertEqual(resolution.min_price, 99.0)

    def test_resolve_touch_market_detects_below_touch(self) -> None:
        market = SyntheticBTCMarket(
            market_id="synthetic-touch-below",
            question="Will BTC touch below?",
            event_type="touch",
            direction="below",
            target_price=95.0,
            decision_time_utc=datetime(2026, 1, 1, tzinfo=timezone.utc),
            deadline_utc=datetime(2026, 1, 4, tzinfo=timezone.utc),
            initial_price=100.0,
        )
        price_data = pd.DataFrame(
            {
                "timestamp_utc": pd.to_datetime(["2026-01-02", "2026-01-03"], utc=True),
                "high": [101.0, 102.0],
                "low": [96.0, 94.0],
            }
        )

        resolution = resolve_touch_market(price_data, market=market)

        self.assertTrue(resolution.touched)
        self.assertEqual(resolution.touch_time_utc, datetime(2026, 1, 3, tzinfo=timezone.utc))

    def test_resolve_touch_market_rejects_invalid_inputs(self) -> None:
        market = SyntheticBTCMarket(
            market_id="synthetic-terminal",
            question="Will BTC close above?",
            event_type="terminal",
            direction="above",
            target_price=105.0,
            decision_time_utc=datetime(2026, 1, 1, tzinfo=timezone.utc),
            deadline_utc=datetime(2026, 1, 4, tzinfo=timezone.utc),
            initial_price=100.0,
        )
        price_data = pd.DataFrame(
            {
                "timestamp_utc": pd.to_datetime(["2026-01-02"], utc=True),
                "high": [101.0],
                "low": [99.0],
            }
        )

        with self.assertRaises(ValueError):
            resolve_touch_market(price_data, market=market)


class BacktestMetricsTests(unittest.TestCase):
    def test_calculate_binary_trade_pnl_handles_yes_and_no_outcomes(self) -> None:
        self.assertEqual(
            calculate_binary_trade_pnl(side="BUY_YES", entry_price=0.5, size_usd=10.0, resolved_yes=True),
            10.0,
        )
        self.assertEqual(
            calculate_binary_trade_pnl(side="BUY_NO", entry_price=0.25, size_usd=10.0, resolved_yes=False),
            30.0,
        )
        self.assertEqual(
            calculate_binary_trade_pnl(side="BUY_YES", entry_price=0.5, size_usd=10.0, resolved_yes=False),
            -10.0,
        )

    def test_summarize_backtest_metrics_calculates_core_metrics(self) -> None:
        metrics = summarize_backtest_metrics([10.0, -5.0, -2.0, 7.0], initial_bankroll_usd=100.0, exposures_usd=[10, 5])

        self.assertIsInstance(metrics, BacktestMetrics)
        self.assertAlmostEqual(metrics.total_return, 0.10)
        self.assertEqual(metrics.win_rate, 0.5)
        self.assertEqual(metrics.average_win, 8.5)
        self.assertEqual(metrics.average_loss, -3.5)
        self.assertEqual(metrics.profit_factor, 17 / 7)
        self.assertEqual(metrics.largest_loss, -5.0)
        self.assertEqual(metrics.losing_streak, 2)
        self.assertEqual(metrics.number_of_trades, 4)
        self.assertEqual(metrics.exposure, 0.15)

    def test_summarize_backtest_metrics_handles_no_trades(self) -> None:
        metrics = summarize_backtest_metrics([], initial_bankroll_usd=100.0)

        self.assertEqual(metrics.number_of_trades, 0)
        self.assertEqual(metrics.total_return, 0.0)


if __name__ == "__main__":
    unittest.main()
