import io
import unittest

from src.main import explain_market, main


class FakeGammaClient:
    def __init__(self, market):
        self.market = market
        self.calls = []

    def get_market(self, market_id):
        self.calls.append(market_id)
        return self.market


class MainExplainCliTests(unittest.TestCase):
    def test_explain_market_returns_parser_fields(self) -> None:
        client = FakeGammaClient(_market())

        explanation = explain_market("btc-120k", client=client)

        self.assertEqual(client.calls, ["btc-120k"])
        self.assertEqual(explanation["asset"], "BTC")
        self.assertEqual(explanation["target_price"], 120000.0)
        self.assertEqual(explanation["event_type"], "terminal")

    def test_main_explain_outputs_read_only_explanation(self) -> None:
        output = io.StringIO()

        exit_code = main(["explain", "--market-id", "btc-120k"], out=output, client=FakeGammaClient(_market()))

        self.assertEqual(exit_code, 0)
        text = output.getvalue()
        self.assertIn("read-only, paper-only", text)
        self.assertIn("market_id: btc-120k", text)
        self.assertIn("target_price: 120000.0", text)
        self.assertIn("event_type: terminal", text)


def _market() -> dict[str, object]:
    return {
        "id": "btc-120k",
        "question": "Will Bitcoin close above $120,000 on June 30, 2026?",
        "outcomes": '["Yes", "No"]',
        "outcomePrices": '["0.40", "0.60"]',
    }


if __name__ == "__main__":
    unittest.main()
