import io
import unittest

from src.main import main, run_synthetic_backtest


class MainBacktestCliTests(unittest.TestCase):
    def test_run_synthetic_backtest_returns_metrics(self) -> None:
        metrics = run_synthetic_backtest(rows=12, initial_bankroll_usd=1000.0, size_usd=10.0)

        self.assertGreater(metrics.number_of_trades, 0)
        self.assertGreaterEqual(metrics.win_rate, 0.0)
        self.assertLessEqual(metrics.win_rate, 1.0)

    def test_main_backtest_outputs_offline_metrics(self) -> None:
        output = io.StringIO()

        exit_code = main(["backtest", "--rows", "12", "--bankroll-usd", "1000", "--size-usd", "10"], out=output)

        self.assertEqual(exit_code, 0)
        text = output.getvalue()
        self.assertIn("offline, paper-only", text)
        self.assertIn("number_of_trades:", text)
        self.assertIn("total_return:", text)


if __name__ == "__main__":
    unittest.main()
