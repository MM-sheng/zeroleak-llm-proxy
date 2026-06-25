import unittest
from datetime import timezone

from src.polymarket.market_scanner import (
    filter_tradeable_markets,
    search_btc_markets,
    standardize_markets,
)


class FakeGammaClient:
    def __init__(self, markets):
        self.markets = markets
        self.calls = []

    def get_markets(self, **params):
        self.calls.append(params)
        return self.markets


class Phase2MarketScannerMockTests(unittest.TestCase):
    def test_mock_gamma_pipeline_finds_standardizes_and_filters_btc_markets(self) -> None:
        client = FakeGammaClient(
            [
                {
                    "id": "btc-liquid",
                    "question": "Will Bitcoin close above $120,000 on June 30?",
                    "slug": "bitcoin-close-above-120k-june-30",
                    "outcomes": '["Yes", "No"]',
                    "outcomePrices": '["0.36", "0.64"]',
                    "volumeNum": "50000",
                    "liquidityNum": "1250.5",
                    "endDate": "2026-06-30T23:59:00Z",
                    "active": "true",
                    "closed": "false",
                },
                {
                    "id": "btc-illiquid",
                    "title": "BTC above $150,000 this week?",
                    "outcomes": ["No", "Yes"],
                    "outcomePrices": ["0.80", "0.20"],
                    "volume": "100",
                    "liquidity": "4.99",
                    "end_date": "2026-07-01T00:00:00+00:00",
                    "active": True,
                    "closed": False,
                },
                {
                    "id": "btc-closed",
                    "description": "A bitcoin market that has already closed.",
                    "outcomes": ["Yes", "No"],
                    "outcomePrices": ["0.10", "0.90"],
                    "liquidityNum": "2500",
                    "active": True,
                    "closed": True,
                },
                {
                    "id": "eth-market",
                    "question": "Will ETH close above $5,000 on June 30?",
                    "outcomes": ["Yes", "No"],
                    "outcomePrices": ["0.42", "0.58"],
                    "liquidityNum": "2000",
                    "active": True,
                    "closed": False,
                },
            ]
        )

        raw_markets = search_btc_markets(client, active=True, limit=100)
        standardized = standardize_markets(raw_markets)
        tradeable = filter_tradeable_markets(standardized, min_liquidity=10.0)

        self.assertEqual(client.calls, [{"active": True, "limit": 100}])
        self.assertEqual([market["id"] for market in raw_markets], ["btc-liquid", "btc-illiquid", "btc-closed"])
        self.assertEqual([market["market_id"] for market in tradeable], ["btc-liquid"])
        self.assertEqual(tradeable[0]["yes_price"], 0.36)
        self.assertEqual(tradeable[0]["no_price"], 0.64)
        self.assertEqual(tradeable[0]["liquidity"], 1250.5)
        self.assertEqual(tradeable[0]["end_date_utc"].tzinfo, timezone.utc)
        self.assertIs(tradeable[0]["raw"], client.markets[0])

    def test_mock_gamma_pipeline_handles_empty_search_results(self) -> None:
        client = FakeGammaClient(
            [
                {
                    "id": "eth-market",
                    "question": "Will ETH close above $5,000?",
                    "outcomes": ["Yes", "No"],
                    "outcomePrices": ["0.50", "0.50"],
                    "liquidityNum": "2000",
                    "active": True,
                    "closed": False,
                }
            ]
        )

        raw_markets = search_btc_markets(client)
        standardized = standardize_markets(raw_markets)
        tradeable = filter_tradeable_markets(standardized)

        self.assertEqual(raw_markets, [])
        self.assertEqual(standardized, [])
        self.assertEqual(tradeable, [])


if __name__ == "__main__":
    unittest.main()
