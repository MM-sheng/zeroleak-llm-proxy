import math
import unittest

import numpy as np
import pandas as pd

from src.data.btc_features import (
    add_distance_to_target_price,
    add_realized_volatility,
    add_returns,
)


class BTCReturnFeatureTests(unittest.TestCase):
    def test_add_returns_uses_prior_close_only(self) -> None:
        source = pd.DataFrame(
            {
                "timestamp_utc": pd.to_datetime(
                    ["2026-01-01", "2026-01-02", "2026-01-03"], utc=True
                ),
                "open": [100.0, 110.0, 99.0],
                "high": [111.0, 112.0, 121.0],
                "low": [99.0, 98.0, 98.0],
                "close": [100.0, 110.0, 99.0],
                "volume": [1.0, 2.0, 3.0],
            }
        )

        result = add_returns(source)

        self.assertTrue(math.isnan(result.loc[0, "return_1_period"]))
        self.assertAlmostEqual(result.loc[1, "return_1_period"], 0.10)
        self.assertAlmostEqual(result.loc[2, "return_1_period"], -0.10)
        self.assertAlmostEqual(result.loc[1, "log_return_1_period"], math.log(1.10))
        self.assertAlmostEqual(result.loc[2, "log_return_1_period"], math.log(0.90))
        self.assertEqual(list(source.columns), ["timestamp_utc", "open", "high", "low", "close", "volume"])

    def test_add_returns_rejects_missing_close(self) -> None:
        source = pd.DataFrame({"timestamp_utc": pd.to_datetime(["2026-01-01"], utc=True)})

        with self.assertRaises(ValueError):
            add_returns(source)

    def test_add_returns_rejects_non_positive_close(self) -> None:
        source = pd.DataFrame(
            {
                "timestamp_utc": pd.to_datetime(["2026-01-01"], utc=True),
                "close": [0.0],
            }
        )

        with self.assertRaises(ValueError):
            add_returns(source)

    def test_add_realized_volatility_uses_trailing_log_returns(self) -> None:
        source = pd.DataFrame(
            {
                "timestamp_utc": pd.to_datetime(
                    ["2026-01-01", "2026-01-02", "2026-01-03", "2026-01-04"], utc=True
                ),
                "open": [100.0, 110.0, 121.0, 108.9],
                "high": [111.0, 122.0, 122.0, 110.0],
                "low": [99.0, 109.0, 108.0, 98.0],
                "close": [100.0, 110.0, 121.0, 108.9],
                "volume": [1.0, 2.0, 3.0, 4.0],
            }
        )

        result = add_realized_volatility(source, window=2, periods_per_year=365)
        returns = np.log(pd.Series([100.0, 110.0, 121.0, 108.9]) / pd.Series([100.0, 110.0, 121.0, 108.9]).shift(1))
        expected = returns.rolling(window=2, min_periods=2).std() * np.sqrt(365)

        self.assertTrue(math.isnan(result.loc[0, "realized_volatility_2_period"]))
        self.assertTrue(math.isnan(result.loc[1, "realized_volatility_2_period"]))
        self.assertAlmostEqual(result.loc[2, "realized_volatility_2_period"], expected.loc[2])
        self.assertAlmostEqual(result.loc[3, "realized_volatility_2_period"], expected.loc[3])
        self.assertNotIn("log_return_1_period", source.columns)

    def test_add_realized_volatility_reuses_existing_log_returns(self) -> None:
        source = pd.DataFrame(
            {
                "timestamp_utc": pd.to_datetime(["2026-01-01", "2026-01-02", "2026-01-03"], utc=True),
                "close": [100.0, 100.0, 100.0],
                "log_return_1_period": [float("nan"), 0.01, -0.02],
            }
        )

        result = add_realized_volatility(
            source,
            window=2,
            periods_per_year=10,
            output_column="rv_custom",
        )
        expected = pd.Series([float("nan"), 0.01, -0.02]).rolling(window=2, min_periods=2).std() * np.sqrt(10)

        self.assertAlmostEqual(result.loc[2, "rv_custom"], expected.loc[2])

    def test_add_realized_volatility_rejects_invalid_window(self) -> None:
        source = pd.DataFrame(
            {
                "timestamp_utc": pd.to_datetime(["2026-01-01"], utc=True),
                "close": [100.0],
            }
        )

        with self.assertRaises(ValueError):
            add_realized_volatility(source, window=1, periods_per_year=365)

    def test_add_realized_volatility_rejects_invalid_periods_per_year(self) -> None:
        source = pd.DataFrame(
            {
                "timestamp_utc": pd.to_datetime(["2026-01-01"], utc=True),
                "close": [100.0],
            }
        )

        with self.assertRaises(ValueError):
            add_realized_volatility(source, window=2, periods_per_year=0)


class BTCTargetDistanceFeatureTests(unittest.TestCase):
    def test_add_distance_to_target_price_adds_usd_and_pct_distance(self) -> None:
        source = pd.DataFrame(
            {
                "timestamp_utc": pd.to_datetime(["2026-01-01", "2026-01-02"], utc=True),
                "close": [100.0, 125.0],
            }
        )

        result = add_distance_to_target_price(source, target_price=120.0)

        self.assertEqual(result.loc[0, "target_price_usd"], 120.0)
        self.assertEqual(result.loc[0, "distance_to_target_price_usd"], 20.0)
        self.assertAlmostEqual(result.loc[0, "distance_to_target_price_pct"], 0.20)
        self.assertEqual(result.loc[1, "distance_to_target_price_usd"], -5.0)
        self.assertAlmostEqual(result.loc[1, "distance_to_target_price_pct"], -0.04)
        self.assertNotIn("distance_to_target_price_usd", source.columns)

    def test_add_distance_to_target_price_rejects_invalid_target(self) -> None:
        source = pd.DataFrame(
            {
                "timestamp_utc": pd.to_datetime(["2026-01-01"], utc=True),
                "close": [100.0],
            }
        )

        with self.assertRaises(ValueError):
            add_distance_to_target_price(source, target_price=0.0)

    def test_add_distance_to_target_price_rejects_missing_close(self) -> None:
        source = pd.DataFrame({"timestamp_utc": pd.to_datetime(["2026-01-01"], utc=True)})

        with self.assertRaises(ValueError):
            add_distance_to_target_price(source, target_price=120.0)

    def test_add_distance_to_target_price_rejects_non_positive_close(self) -> None:
        source = pd.DataFrame(
            {
                "timestamp_utc": pd.to_datetime(["2026-01-01"], utc=True),
                "close": [-1.0],
            }
        )

        with self.assertRaises(ValueError):
            add_distance_to_target_price(source, target_price=120.0)


if __name__ == "__main__":
    unittest.main()
