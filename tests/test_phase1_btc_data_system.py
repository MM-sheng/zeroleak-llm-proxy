import math
import unittest

import pandas as pd

from src.data.btc_features import (
    add_distance_to_target_price,
    add_realized_volatility,
    add_returns,
)
from src.data.btc_price_loader import BTCPriceLoader


class Phase1BTCDataSystemTests(unittest.TestCase):
    def test_loader_and_feature_pipeline_stays_offline_and_canonical(self) -> None:
        calls = []
        source = pd.DataFrame(
            {
                "Open": [100.0, 110.0, 121.0, 108.9],
                "High": [111.0, 122.0, 122.0, 110.0],
                "Low": [99.0, 109.0, 108.0, 98.0],
                "Close": [100.0, 110.0, 121.0, 108.9],
                "Volume": [1.0, 2.0, 3.0, 4.0],
            },
            index=pd.to_datetime(
                ["2026-01-01", "2026-01-02", "2026-01-03", "2026-01-04"],
                utc=True,
            ),
        )

        def fake_downloader(**kwargs):
            calls.append(kwargs)
            return source

        loaded = BTCPriceLoader(downloader=fake_downloader).load_history(period="4d")
        with_returns = add_returns(loaded)
        with_volatility = add_realized_volatility(
            with_returns,
            window=2,
            periods_per_year=365,
        )
        result = add_distance_to_target_price(with_volatility, target_price=120.0)

        self.assertEqual(calls[0]["tickers"], "BTC-USD")
        self.assertEqual(
            list(loaded.columns),
            ["timestamp_utc", "open", "high", "low", "close", "volume"],
        )
        self.assertEqual(str(result.loc[0, "timestamp_utc"].tz), "UTC")
        self.assertAlmostEqual(result.loc[1, "return_1_period"], 0.10)
        self.assertFalse(math.isnan(result.loc[2, "realized_volatility_2_period"]))
        self.assertAlmostEqual(result.loc[3, "distance_to_target_price_usd"], 11.1)
        self.assertAlmostEqual(result.loc[3, "distance_to_target_price_pct"], 11.1 / 108.9)

    def test_feature_pipeline_does_not_mutate_loader_output(self) -> None:
        loaded = pd.DataFrame(
            {
                "timestamp_utc": pd.to_datetime(["2026-01-01", "2026-01-02"], utc=True),
                "open": [100.0, 110.0],
                "high": [111.0, 112.0],
                "low": [99.0, 109.0],
                "close": [100.0, 110.0],
                "volume": [1.0, 2.0],
            }
        )

        add_distance_to_target_price(add_returns(loaded), target_price=120.0)

        self.assertEqual(
            list(loaded.columns),
            ["timestamp_utc", "open", "high", "low", "close", "volume"],
        )


if __name__ == "__main__":
    unittest.main()
