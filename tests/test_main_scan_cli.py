import io
import unittest

from src.main import main, scan_btc_tradeable_markets


class FakeGammaClient:
    def __init__(self, markets):
        self.markets = markets
        self.calls = []

    def get_markets(self, **params):
        self.calls.append(params)
        return self.markets


class MainScanCliTests(unittest.TestCase):
    def test_scan_pipeline_returns_tradeable_btc_markets(self) -> None:
        client = FakeGammaClient([_btc_market("keep", liquidity="20"), _btc_market("skip", liquidity="1")])

        markets = scan_btc_tradeable_markets(client=client, limit=50, min_liquidity=10.0)

        self.assertEqual(client.calls, [{"active": True, "limit": 50}])
        self.assertEqual([market["market_id"] for market in markets], ["keep"])

    def test_main_scan_outputs_read_only_table(self) -> None:
        client = FakeGammaClient([_btc_market("btc-100k", liquidity="25")])
        output = io.StringIO()

        exit_code = main(["scan", "--limit", "25", "--min-liquidity", "10"], out=output, client=client)

        self.assertEqual(exit_code, 0)
        text = output.getvalue()
        self.assertIn("read-only, paper-only", text)
        self.assertIn("btc-100k", text)
        self.assertIn("| market_id | question | yes_price | no_price | liquidity |", text)

    def test_main_scan_handles_no_tradeable_markets(self) -> None:
        client = FakeGammaClient([_btc_market("too-small", liquidity="1")])
        output = io.StringIO()

        exit_code = main(["scan", "--min-liquidity", "10"], out=output, client=client)

        self.assertEqual(exit_code, 0)
        self.assertIn("No tradeable BTC markets found.", output.getvalue())


def _btc_market(market_id: str, *, liquidity: str) -> dict[str, object]:
    return {
        "id": market_id,
        "question": "Will Bitcoin hit $100,000 this week?",
        "slug": f"{market_id}-bitcoin",
        "outcomes": '["Yes", "No"]',
        "outcomePrices": '["0.50", "0.50"]',
        "liquidityNum": liquidity,
        "active": "true",
        "closed": "false",
    }


if __name__ == "__main__":
    unittest.main()
