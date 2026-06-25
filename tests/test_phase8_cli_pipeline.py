import io
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from src.main import main


class FakeGammaClient:
    def get_markets(self, **params):
        return [_market()]

    def get_market(self, market_id):
        return _market()


class Phase8CliPipelineTests(unittest.TestCase):
    def test_phase8_cli_commands_run_offline_with_injected_data(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            journal = root / "journal.jsonl"
            report = root / "daily_report.md"
            client = FakeGammaClient()
            price_data = _price_data()

            commands = [
                (["scan"], {"client": client}),
                (["explain", "--market-id", "btc-120k"], {"client": client}),
                (["model", "--market-id", "btc-120k", "--vol-window", "5", "--n-paths", "50"], {"client": client, "price_data": price_data}),
                (
                    [
                        "paper",
                        "--journal",
                        str(journal),
                        "--market-id",
                        "btc-120k",
                        "--question",
                        "Will Bitcoin close above $120,000 on June 30, 2026?",
                        "--action",
                        "HOLD",
                        "--model-probability",
                        "0.50",
                    ],
                    {},
                ),
                (["report", "--journal", str(journal), "--output", str(report)], {}),
                (["backtest", "--rows", "12"], {}),
            ]

            for argv, kwargs in commands:
                with self.subTest(argv=argv):
                    self.assertEqual(main(argv, out=io.StringIO(), **kwargs), 0)

            self.assertTrue(report.exists())


def _market() -> dict[str, object]:
    return {
        "id": "btc-120k",
        "question": "Will Bitcoin close above $120,000 on June 30, 2026?",
        "slug": "btc-120k",
        "outcomes": '["Yes", "No"]',
        "outcomePrices": '["0.40", "0.60"]',
        "liquidityNum": "100",
        "active": True,
        "closed": False,
    }


def _price_data() -> pd.DataFrame:
    dates = pd.date_range("2026-01-01", periods=40, freq="D", tz="UTC")
    close = [100000.0 + index * 100.0 for index in range(40)]
    return pd.DataFrame(
        {
            "timestamp_utc": dates,
            "open": close,
            "high": [value + 100.0 for value in close],
            "low": [value - 100.0 for value in close],
            "close": close,
            "volume": [1.0 for _ in close],
        }
    )


if __name__ == "__main__":
    unittest.main()
