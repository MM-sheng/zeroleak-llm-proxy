import unittest
from datetime import datetime, timezone

import pandas as pd

from src.backtest import (
    calculate_binary_trade_pnl,
    estimate_prior_volatility,
    generate_weekly_touch_markets,
    resolve_touch_market,
    summarize_backtest_metrics,
)


class Phase6BacktestPipelineTests(unittest.TestCase):
    def test_phase6_synthetic_backtest_pipeline_runs_offline(self) -> None:
        price_data = pd.DataFrame(
            {
                "timestamp_utc": pd.to_datetime(
                    ["2026-01-01", "2026-01-02", "2026-01-03", "2026-01-04", "2026-01-05"],
                    utc=True,
                ),
                "open": [100.0, 101.0, 102.0, 103.0, 104.0],
                "high": [101.0, 102.0, 103.0, 106.0, 110.0],
                "low": [99.0, 100.0, 101.0, 102.0, 103.0],
                "close": [100.0, 101.0, 102.0, 103.0, 104.0],
                "volume": [1.0, 1.0, 1.0, 1.0, 1.0],
            }
        )
        market = generate_weekly_touch_markets(price_data.iloc[[3]])[0]
        volatility = estimate_prior_volatility(
            price_data,
            decision_time_utc=market.decision_time_utc,
            window=2,
        )
        resolution = resolve_touch_market(price_data, market=market)
        pnl = calculate_binary_trade_pnl(
            side="BUY_YES",
            entry_price=0.50,
            size_usd=10.0,
            resolved_yes=resolution.touched,
        )
        metrics = summarize_backtest_metrics([pnl], initial_bankroll_usd=100.0, exposures_usd=[10.0])

        self.assertEqual(volatility.as_of_utc, datetime(2026, 1, 3, tzinfo=timezone.utc))
        self.assertTrue(resolution.touched)
        self.assertEqual(metrics.number_of_trades, 1)
        self.assertGreater(metrics.total_return, 0.0)


if __name__ == "__main__":
    unittest.main()
