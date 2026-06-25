import io
import unittest

import pandas as pd

from src.main import main, model_market_probability


class FakeGammaClient:
    def __init__(self, market):
        self.market = market
        self.calls = []

    def get_market(self, market_id):
        self.calls.append(market_id)
        return self.market


class MainModelCliTests(unittest.TestCase):
    def test_model_market_probability_runs_offline_with_injected_data(self) -> None:
        client = FakeGammaClient(_market())

        result = model_market_probability(
            market_id="btc-145",
            client=client,
            price_data=_price_data(),
            volatility_window=5,
            n_paths=100,
            random_seed=7,
        )

        self.assertEqual(client.calls, ["btc-145"])
        self.assertEqual(result["market_id"], "btc-145")
        self.assertEqual(result["event_type"], "terminal")
        self.assertGreaterEqual(result["ensemble_probability"], 0.0)
        self.assertLessEqual(result["ensemble_probability"], 1.0)

    def test_main_model_outputs_read_only_probabilities(self) -> None:
        output = io.StringIO()

        exit_code = main(
            ["model", "--market-id", "btc-145", "--vol-window", "5", "--n-paths", "100", "--seed", "7"],
            out=output,
            client=FakeGammaClient(_market()),
            price_data=_price_data(),
        )

        self.assertEqual(exit_code, 0)
        text = output.getvalue()
        self.assertIn("read-only, paper-only", text)
        self.assertIn("market_id: btc-145", text)
        self.assertIn("monte_carlo_probability:", text)
        self.assertIn("bootstrap_probability:", text)
        self.assertIn("ensemble_probability:", text)

    def test_main_model_returns_error_for_unparseable_market(self) -> None:
        output = io.StringIO()
        client = FakeGammaClient({"id": "bad", "question": "Will something happen?"})

        exit_code = main(["model", "--market-id", "bad"], out=output, client=client, price_data=_price_data())

        self.assertEqual(exit_code, 1)
        self.assertIn("model failed:", output.getvalue())


def _market() -> dict[str, object]:
    return {
        "id": "btc-145",
        "question": "Will Bitcoin close above $145 on March 1, 2026?",
        "outcomes": '["Yes", "No"]',
        "outcomePrices": '["0.45", "0.55"]',
        "active": True,
        "closed": False,
    }


def _price_data() -> pd.DataFrame:
    dates = pd.date_range("2026-01-01", periods=40, freq="D", tz="UTC")
    close = [100.0 + index for index in range(40)]
    return pd.DataFrame(
        {
            "timestamp_utc": dates,
            "open": close,
            "high": [value + 1.0 for value in close],
            "low": [value - 1.0 for value in close],
            "close": close,
            "volume": [1.0 for _ in close],
        }
    )


if __name__ == "__main__":
    unittest.main()
