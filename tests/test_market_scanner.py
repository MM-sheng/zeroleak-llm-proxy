import unittest
from datetime import timezone

from src.polymarket.market_scanner import (
    MARKET_SCHEMA,
    filter_tradeable_markets,
    search_btc_markets,
    standardize_market,
    standardize_markets,
)


class FakeGammaClient:
    def __init__(self, markets):
        self.markets = markets
        self.calls = []

    def get_markets(self, **params):
        self.calls.append(params)
        return self.markets


class MarketScannerTests(unittest.TestCase):
    def test_search_btc_markets_matches_question_and_slug(self) -> None:
        client = FakeGammaClient(
            [
                {"id": "1", "question": "Will Bitcoin hit $120,000?"},
                {"id": "2", "slug": "btc-above-100k-june"},
                {"id": "3", "question": "Will ETH hit $5,000?"},
            ]
        )

        markets = search_btc_markets(client, limit=100, active=True)

        self.assertEqual([market["id"] for market in markets], ["1", "2"])
        self.assertEqual(client.calls[0], {"limit": 100, "active": True})

    def test_search_btc_markets_matches_title_and_description(self) -> None:
        client = FakeGammaClient(
            [
                {"id": "1", "title": "BTC all time high"},
                {"id": "2", "description": "Market about bitcoin dominance"},
                {"id": "3", "title": "Solana ETF approval"},
            ]
        )

        markets = search_btc_markets(client)

        self.assertEqual([market["id"] for market in markets], ["1", "2"])

    def test_search_btc_markets_accepts_custom_keywords(self) -> None:
        client = FakeGammaClient(
            [
                {"id": "1", "question": "Will XBT trade above $100,000?"},
                {"id": "2", "question": "Will Bitcoin trade above $100,000?"},
            ]
        )

        markets = search_btc_markets(client, keywords=("xbt",))

        self.assertEqual([market["id"] for market in markets], ["1"])

    def test_search_btc_markets_rejects_empty_keywords(self) -> None:
        client = FakeGammaClient([])

        with self.assertRaises(ValueError):
            search_btc_markets(client, keywords=(" ",))

    def test_search_btc_markets_ignores_non_dict_entries(self) -> None:
        client = FakeGammaClient(
            [
                {"id": "1", "question": "Will BTC rally?"},
                "not-a-market",
                None,
            ]
        )

        markets = search_btc_markets(client)

        self.assertEqual(markets, [{"id": "1", "question": "Will BTC rally?"}])

    def test_standardize_market_maps_common_gamma_fields(self) -> None:
        raw = {
            "id": "123",
            "question": "Will Bitcoin hit $120,000?",
            "slug": "bitcoin-120k",
            "outcomes": '["Yes", "No"]',
            "outcomePrices": '["0.42", "0.58"]',
            "volumeNum": "1234.5",
            "liquidityNum": 456.7,
            "endDate": "2026-06-30T00:00:00Z",
            "active": "true",
            "closed": 0,
        }

        market = standardize_market(raw)

        self.assertEqual(list(market.keys()), list(MARKET_SCHEMA))
        self.assertEqual(market["market_id"], "123")
        self.assertEqual(market["question"], "Will Bitcoin hit $120,000?")
        self.assertEqual(market["slug"], "bitcoin-120k")
        self.assertEqual(market["outcomes"], ["Yes", "No"])
        self.assertEqual(market["outcome_prices"], ["0.42", "0.58"])
        self.assertEqual(market["yes_price"], 0.42)
        self.assertEqual(market["no_price"], 0.58)
        self.assertEqual(market["volume"], 1234.5)
        self.assertEqual(market["liquidity"], 456.7)
        self.assertEqual(market["end_date_utc"].tzinfo, timezone.utc)
        self.assertTrue(market["active"])
        self.assertFalse(market["closed"])
        self.assertIs(market["raw"], raw)

    def test_standardize_market_uses_fallback_fields_and_preserves_unknowns(self) -> None:
        raw = {
            "condition_id": "condition-1",
            "title": "BTC above 100k?",
            "outcomes": ("Yes", "No"),
            "volume": "not-a-number",
            "active": None,
        }

        market = standardize_market(raw)

        self.assertEqual(market["market_id"], "condition-1")
        self.assertEqual(market["question"], "BTC above 100k?")
        self.assertEqual(market["outcomes"], ["Yes", "No"])
        self.assertIsNone(market["volume"])
        self.assertIsNone(market["liquidity"])
        self.assertIsNone(market["end_date_utc"])
        self.assertIsNone(market["active"])

    def test_standardize_market_prefers_explicit_yes_no_prices(self) -> None:
        raw = {
            "id": "123",
            "question": "Will BTC rally?",
            "outcomes": ["Yes", "No"],
            "outcomePrices": ["0.20", "0.80"],
            "yesPrice": "0.33",
            "noPrice": 0.67,
        }

        market = standardize_market(raw)

        self.assertEqual(market["yes_price"], 0.33)
        self.assertEqual(market["no_price"], 0.67)

    def test_standardize_market_handles_reversed_yes_no_outcome_order(self) -> None:
        raw = {
            "id": "123",
            "question": "Will BTC rally?",
            "outcomes": ["No", "Yes"],
            "outcomePrices": ["0.60", "0.40"],
        }

        market = standardize_market(raw)

        self.assertEqual(market["yes_price"], 0.40)
        self.assertEqual(market["no_price"], 0.60)

    def test_standardize_market_rejects_invalid_probability_values(self) -> None:
        raw = {
            "id": "123",
            "question": "Will BTC rally?",
            "outcomes": ["Yes", "No"],
            "outcomePrices": ["1.20", "-0.10"],
        }

        market = standardize_market(raw)

        self.assertIsNone(market["yes_price"])
        self.assertIsNone(market["no_price"])

    def test_standardize_market_handles_missing_outcome_price_index(self) -> None:
        raw = {
            "id": "123",
            "question": "Will BTC rally?",
            "outcomes": ["Yes", "No"],
            "outcomePrices": ["0.50"],
        }

        market = standardize_market(raw)

        self.assertEqual(market["yes_price"], 0.50)
        self.assertIsNone(market["no_price"])

    def test_standardize_markets_normalizes_iterable(self) -> None:
        markets = standardize_markets(
            [
                {"id": "1", "question": "Will BTC rally?"},
                {"id": "2", "question": "Will Bitcoin fall?"},
            ]
        )

        self.assertEqual([market["market_id"] for market in markets], ["1", "2"])

    def test_standardize_market_rejects_non_dict(self) -> None:
        with self.assertRaises(TypeError):
            standardize_market("not-a-market")

    def test_filter_tradeable_markets_keeps_active_open_liquid_markets(self) -> None:
        markets = [
            {"market_id": "keep", "active": True, "closed": False, "liquidity": 100.0},
            {"market_id": "inactive", "active": False, "closed": False, "liquidity": 100.0},
            {"market_id": "closed", "active": True, "closed": True, "liquidity": 100.0},
            {"market_id": "illiquid", "active": True, "closed": False, "liquidity": 9.99},
        ]

        filtered = filter_tradeable_markets(markets, min_liquidity=10.0)

        self.assertEqual([market["market_id"] for market in filtered], ["keep"])

    def test_filter_tradeable_markets_excludes_unknown_status_or_liquidity(self) -> None:
        markets = [
            {"market_id": "unknown-active", "active": None, "closed": False, "liquidity": 100.0},
            {"market_id": "unknown-closed", "active": True, "closed": None, "liquidity": 100.0},
            {"market_id": "unknown-liquidity", "active": True, "closed": False, "liquidity": None},
            {"market_id": "non-dict"},
        ]

        filtered = filter_tradeable_markets(markets)

        self.assertEqual(filtered, [])

    def test_filter_tradeable_markets_accepts_numeric_liquidity_strings(self) -> None:
        markets = [
            {"market_id": "keep", "active": True, "closed": False, "liquidity": "10.5"},
        ]

        filtered = filter_tradeable_markets(markets, min_liquidity=10.0)

        self.assertEqual([market["market_id"] for market in filtered], ["keep"])

    def test_filter_tradeable_markets_rejects_negative_liquidity_threshold(self) -> None:
        with self.assertRaises(ValueError):
            filter_tradeable_markets([], min_liquidity=-1.0)


if __name__ == "__main__":
    unittest.main()
