import math
import unittest
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from src.models import HistoricalVolatilityEstimate, estimate_historical_volatility


class HistoricalVolatilityModelTests(unittest.TestCase):
    def test_estimate_historical_volatility_uses_trailing_log_returns(self) -> None:
        closes = pd.Series([100.0, 105.0, 103.0, 108.0, 112.0])
        data = pd.DataFrame(
            {
                "timestamp_utc": pd.to_datetime(
                    ["2026-01-01", "2026-01-02", "2026-01-03", "2026-01-04", "2026-01-05"],
                    utc=True,
                ),
                "close": closes,
            }
        )

        estimate = estimate_historical_volatility(data, window=3, periods_per_year=365)
        returns = np.log(closes / closes.shift(1)).dropna().tail(3)

        self.assertIsInstance(estimate, HistoricalVolatilityEstimate)
        self.assertAlmostEqual(estimate.annualized_volatility, float(returns.std(ddof=1) * np.sqrt(365)))
        self.assertAlmostEqual(estimate.annualized_mean_log_return, float(returns.mean() * 365))
        self.assertEqual(estimate.window, 3)
        self.assertEqual(estimate.periods_per_year, 365)
        self.assertEqual(estimate.observations, 3)
        self.assertEqual(estimate.latest_close, 112.0)
        self.assertEqual(estimate.as_of_utc, datetime(2026, 1, 5, tzinfo=timezone.utc))
        self.assertEqual(estimate.warnings, ())

    def test_estimate_historical_volatility_sorts_rows_without_using_future_beyond_input(self) -> None:
        data = pd.DataFrame(
            {
                "timestamp_utc": pd.to_datetime(["2026-01-03", "2026-01-01", "2026-01-02"], utc=True),
                "close": [121.0, 100.0, 110.0],
            }
        )

        estimate = estimate_historical_volatility(data, window=2, periods_per_year=10)

        self.assertEqual(estimate.latest_close, 121.0)
        self.assertEqual(estimate.as_of_utc, datetime(2026, 1, 3, tzinfo=timezone.utc))

    def test_estimate_historical_volatility_warns_on_zero_volatility(self) -> None:
        data = pd.DataFrame(
            {
                "timestamp_utc": pd.to_datetime(["2026-01-01", "2026-01-02", "2026-01-03"], utc=True),
                "close": [100.0, 100.0, 100.0],
            }
        )

        estimate = estimate_historical_volatility(data, window=2, periods_per_year=365)

        self.assertEqual(estimate.annualized_volatility, 0.0)
        self.assertIn("zero_volatility", estimate.warnings)

    def test_estimate_historical_volatility_rejects_invalid_inputs(self) -> None:
        valid = pd.DataFrame(
            {
                "timestamp_utc": pd.to_datetime(["2026-01-01", "2026-01-02", "2026-01-03"], utc=True),
                "close": [100.0, 101.0, 102.0],
            }
        )
        invalid_cases = [
            (valid, {"window": 1}),
            (valid, {"window": 2, "periods_per_year": 0}),
            (pd.DataFrame({"timestamp_utc": pd.to_datetime(["2026-01-01"], utc=True)}), {"window": 2}),
            (pd.DataFrame({"timestamp_utc": pd.to_datetime(["2026-01-01"], utc=True), "close": [0.0]}), {"window": 2}),
            (valid.iloc[:2], {"window": 2}),
        ]

        for frame, kwargs in invalid_cases:
            with self.subTest(kwargs=kwargs):
                with self.assertRaises((TypeError, ValueError)):
                    estimate_historical_volatility(frame, **kwargs)


if __name__ == "__main__":
    unittest.main()
