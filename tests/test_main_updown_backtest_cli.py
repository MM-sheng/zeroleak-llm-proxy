import io
import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from src.backtest import BacktestMetrics, CachedUpDownBacktestResult, UpDownBacktestEntry, UpDownWindow
from src.main import main


class MainUpDownBacktestCliTests(unittest.TestCase):
    def test_main_updown_backtest_outputs_cached_metrics(self) -> None:
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
            policy="first_seen",
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
                    "--bankroll-usd",
                    "1000",
                    "--size-usd",
                    "10",
                    "--no-15m",
                ],
                out=output,
            )

        self.assertEqual(exit_code, 0)
        runner.assert_called_once()
        kwargs = runner.call_args.kwargs
        self.assertEqual(kwargs["cache_dir"], "data/test_updown_cache")
        self.assertEqual(kwargs["lookback_minutes"], 30)
        self.assertFalse(kwargs["include_15m"])
        text = output.getvalue()
        self.assertIn("read-only, paper-only", text)
        self.assertIn("windows: 1", text)
        self.assertIn("skipped_windows: 0", text)
        self.assertIn("entries: 1", text)
        self.assertIn("total_return: 0.0100", text)
        self.assertIn("by_policy:", text)
        self.assertIn("first_seen: trades=1", text)
        self.assertIn("by_kind:", text)
        self.assertIn("5m: trades=1", text)


if __name__ == "__main__":
    unittest.main()
