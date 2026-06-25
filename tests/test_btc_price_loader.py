import unittest

import pandas as pd

from src.data.btc_price_loader import BTCPriceLoadError, BTCPriceLoader


class BTCPriceLoaderTests(unittest.TestCase):
    def test_load_history_uses_btc_usd_with_yfinance_arguments(self) -> None:
        calls = []
        source = pd.DataFrame(
            {
                "Open": [100.0],
                "High": [110.0],
                "Low": [95.0],
                "Close": [105.0],
                "Volume": [123.0],
            },
            index=pd.to_datetime(["2026-01-01"], utc=True),
        )

        def fake_downloader(**kwargs):
            calls.append(kwargs)
            return source

        loader = BTCPriceLoader(downloader=fake_downloader, timeout_seconds=12)
        result = loader.load_history(period="5d", interval="1h", auto_adjust=True)

        self.assertEqual(
            list(result.columns),
            ["timestamp_utc", "open", "high", "low", "close", "volume"],
        )
        self.assertEqual(result.loc[0, "close"], 105.0)
        self.assertEqual(calls[0]["tickers"], "BTC-USD")
        self.assertEqual(calls[0]["period"], "5d")
        self.assertEqual(calls[0]["interval"], "1h")
        self.assertTrue(calls[0]["auto_adjust"])
        self.assertFalse(calls[0]["progress"])
        self.assertEqual(calls[0]["timeout"], 12)

    def test_custom_symbol_is_supported(self) -> None:
        def fake_downloader(**kwargs):
            return pd.DataFrame(
                {
                    "Open": [1.0],
                    "High": [1.0],
                    "Low": [1.0],
                    "Close": [1.0],
                    "Volume": [0.0],
                },
                index=pd.to_datetime(["2026-01-01"], utc=True),
            )

        loader = BTCPriceLoader(symbol="BTC-USD", downloader=fake_downloader)

        self.assertFalse(loader.load_history().empty)

    def test_empty_download_raises_loader_error(self) -> None:
        def fake_downloader(**kwargs):
            return pd.DataFrame()

        loader = BTCPriceLoader(downloader=fake_downloader)

        with self.assertRaises(BTCPriceLoadError):
            loader.load_history()

    def test_load_history_rejects_missing_daily_rows_for_requested_interval(self) -> None:
        def fake_downloader(**kwargs):
            return pd.DataFrame(
                {
                    "Open": [100.0, 102.0],
                    "High": [105.0, 108.0],
                    "Low": [99.0, 101.0],
                    "Close": [104.0, 107.0],
                    "Volume": [1.0, 2.0],
                },
                index=pd.to_datetime(["2026-01-01", "2026-01-03"], utc=True),
            )

        loader = BTCPriceLoader(downloader=fake_downloader)

        with self.assertRaises(BTCPriceLoadError):
            loader.load_history(interval="1d")

    def test_invalid_symbol_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            BTCPriceLoader(symbol=" ")

    def test_invalid_timeout_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            BTCPriceLoader(timeout_seconds=0)

    def test_standardize_schema_converts_timestamp_column_to_utc(self) -> None:
        source = pd.DataFrame(
            {
                "Date": ["2026-01-01 12:00:00"],
                "Open": [100.0],
                "High": [105.0],
                "Low": [98.0],
                "Close": [102.0],
                "Volume": [42.0],
            }
        )

        result = BTCPriceLoader.standardize_schema(source)

        self.assertEqual(str(result.loc[0, "timestamp_utc"].tz), "UTC")
        self.assertEqual(result.loc[0, "open"], 100.0)

    def test_standardize_schema_allows_sparse_rows_without_expected_interval(self) -> None:
        source = pd.DataFrame(
            {
                "Open": [100.0, 102.0],
                "High": [105.0, 108.0],
                "Low": [99.0, 101.0],
                "Close": [104.0, 107.0],
                "Volume": [1.0, 2.0],
            },
            index=pd.to_datetime(["2026-01-01", "2026-01-03"], utc=True),
        )

        result = BTCPriceLoader.standardize_schema(source)

        self.assertEqual(len(result), 2)

    def test_standardize_schema_rejects_duplicate_timestamps(self) -> None:
        source = pd.DataFrame(
            {
                "Open": [100.0, 101.0],
                "High": [110.0, 111.0],
                "Low": [95.0, 96.0],
                "Close": [105.0, 106.0],
                "Volume": [1.0, 2.0],
            },
            index=pd.to_datetime(["2026-01-01", "2026-01-01"], utc=True),
        )

        with self.assertRaises(BTCPriceLoadError):
            BTCPriceLoader.standardize_schema(source)

    def test_standardize_schema_rejects_missing_required_column(self) -> None:
        source = pd.DataFrame(
            {"Open": [100.0], "High": [110.0], "Low": [95.0], "Close": [105.0]},
            index=pd.to_datetime(["2026-01-01"], utc=True),
        )

        with self.assertRaises(BTCPriceLoadError):
            BTCPriceLoader.standardize_schema(source)

    def test_standardize_schema_rejects_invalid_prices(self) -> None:
        source = pd.DataFrame(
            {
                "Open": [100.0],
                "High": [110.0],
                "Low": [0.0],
                "Close": [105.0],
                "Volume": [1.0],
            },
            index=pd.to_datetime(["2026-01-01"], utc=True),
        )

        with self.assertRaises(BTCPriceLoadError):
            BTCPriceLoader.standardize_schema(source)

    def test_standardize_schema_rejects_invalid_timestamp(self) -> None:
        source = pd.DataFrame(
            {
                "Date": ["not-a-date"],
                "Open": [100.0],
                "High": [110.0],
                "Low": [95.0],
                "Close": [105.0],
                "Volume": [1.0],
            }
        )

        with self.assertRaises(BTCPriceLoadError):
            BTCPriceLoader.standardize_schema(source)

    def test_standardize_schema_rejects_inconsistent_high_low(self) -> None:
        source = pd.DataFrame(
            {
                "Open": [100.0],
                "High": [99.0],
                "Low": [95.0],
                "Close": [105.0],
                "Volume": [1.0],
            },
            index=pd.to_datetime(["2026-01-01"], utc=True),
        )

        with self.assertRaises(BTCPriceLoadError):
            BTCPriceLoader.standardize_schema(source)

    def test_standardize_schema_flattens_yfinance_multiindex_columns(self) -> None:
        source = pd.DataFrame(
            [[100.0, 110.0, 95.0, 105.0, 1.0]],
            columns=pd.MultiIndex.from_product(
                [["BTC-USD"], ["Open", "High", "Low", "Close", "Volume"]]
            ),
            index=pd.to_datetime(["2026-01-01"], utc=True),
        )

        result = BTCPriceLoader.standardize_schema(source)

        self.assertEqual(result.loc[0, "volume"], 1.0)


if __name__ == "__main__":
    unittest.main()
