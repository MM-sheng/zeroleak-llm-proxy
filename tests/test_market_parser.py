import unittest
from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

from src.parser import ParsedMarket, parse_market_question


class ParsedMarketTests(unittest.TestCase):
    def test_parsed_market_defaults_to_unknown_low_confidence(self) -> None:
        parsed = ParsedMarket()

        self.assertEqual(parsed.asset, "unknown")
        self.assertIsNone(parsed.target_price)
        self.assertEqual(parsed.direction, "unknown")
        self.assertEqual(parsed.event_type, "unknown")
        self.assertIsNone(parsed.deadline_utc)
        self.assertEqual(parsed.confidence, 0.0)
        self.assertEqual(parsed.warnings, ())

    def test_parsed_market_normalizes_asset_deadline_confidence_and_warnings(self) -> None:
        parsed = ParsedMarket(
            asset=" btc ",
            target_price="120000",
            direction="above",
            event_type="terminal",
            deadline_utc=datetime(2026, 6, 30, 16, 0),
            confidence="0.75",
            warnings=["ambiguous close time", 123],
        )

        self.assertEqual(parsed.asset, "BTC")
        self.assertEqual(parsed.target_price, 120000.0)
        self.assertEqual(parsed.deadline_utc.tzinfo, timezone.utc)
        self.assertEqual(parsed.confidence, 0.75)
        self.assertEqual(parsed.warnings, ("ambiguous close time", "123"))

    def test_parsed_market_converts_aware_deadline_to_utc(self) -> None:
        eastern = timezone.utc
        parsed = ParsedMarket(deadline_utc=datetime(2026, 6, 30, 23, 0, tzinfo=eastern))

        self.assertEqual(parsed.deadline_utc.tzinfo, timezone.utc)

    def test_parsed_market_rejects_invalid_fields(self) -> None:
        invalid_cases = [
            {"target_price": 0},
            {"direction": "over"},
            {"event_type": "settles"},
            {"confidence": -0.01},
            {"confidence": 1.01},
        ]

        for kwargs in invalid_cases:
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    ParsedMarket(**kwargs)

    def test_parsed_market_is_immutable(self) -> None:
        parsed = ParsedMarket(asset="BTC")

        with self.assertRaises(FrozenInstanceError):
            parsed.asset = "ETH"


class ParseMarketQuestionTests(unittest.TestCase):
    def test_parse_market_question_extracts_common_terminal_btc_market(self) -> None:
        parsed = parse_market_question(
            "Will Bitcoin close above $120,000 on June 30, 2026?",
            reference_time_utc=datetime(2026, 6, 24, tzinfo=timezone.utc),
        )

        self.assertEqual(parsed.asset, "BTC")
        self.assertEqual(parsed.target_price, 120000.0)
        self.assertEqual(parsed.direction, "above")
        self.assertEqual(parsed.event_type, "terminal")
        self.assertEqual(parsed.deadline_utc, datetime(2026, 6, 30, 23, 59, 59, tzinfo=timezone.utc))
        self.assertEqual(parsed.confidence, 1.0)
        self.assertEqual(parsed.warnings, ())

    def test_parse_market_question_extracts_touch_market_with_k_suffix(self) -> None:
        parsed = parse_market_question(
            "Will BTC hit 100k by July 4?",
            reference_time_utc=datetime(2026, 6, 24, tzinfo=timezone.utc),
        )

        self.assertEqual(parsed.target_price, 100000.0)
        self.assertEqual(parsed.direction, "unknown")
        self.assertEqual(parsed.event_type, "touch")
        self.assertEqual(parsed.deadline_utc, datetime(2026, 7, 4, 23, 59, 59, tzinfo=timezone.utc))
        self.assertIn("direction_not_detected", parsed.warnings)

    def test_parse_market_question_treats_be_above_on_date_as_terminal(self) -> None:
        parsed = parse_market_question(
            "Will BTC be above $100,000 on July 4?",
            reference_time_utc=datetime(2026, 6, 24, tzinfo=timezone.utc),
        )

        self.assertEqual(parsed.event_type, "terminal")
        self.assertNotIn("event_type_not_detected", parsed.warnings)

    def test_parse_market_question_treats_trade_above_as_touch(self) -> None:
        parsed = parse_market_question(
            "Will BTC trade above $100,000 before July 4?",
            reference_time_utc=datetime(2026, 6, 24, tzinfo=timezone.utc),
        )

        self.assertEqual(parsed.event_type, "touch")
        self.assertNotIn("event_type_not_detected", parsed.warnings)

    def test_parse_market_question_prefers_terminal_when_event_type_conflicts(self) -> None:
        parsed = parse_market_question(
            "Will BTC hit $100,000 and close above $100,000 on July 4?",
            reference_time_utc=datetime(2026, 6, 24, tzinfo=timezone.utc),
        )

        self.assertEqual(parsed.event_type, "terminal")
        self.assertIn("event_type_conflict_terminal_preferred", parsed.warnings)

    def test_parse_market_question_extracts_below_market(self) -> None:
        parsed = parse_market_question(
            "Will BTC close below $80,000 on Dec 31?",
            reference_time_utc=datetime(2026, 6, 24, tzinfo=timezone.utc),
        )

        self.assertEqual(parsed.direction, "below")
        self.assertEqual(parsed.event_type, "terminal")
        self.assertEqual(parsed.deadline_utc, datetime(2026, 12, 31, 23, 59, 59, tzinfo=timezone.utc))

    def test_parse_market_question_rolls_yearless_past_deadline_forward(self) -> None:
        parsed = parse_market_question(
            "Will BTC close above $120,000 on June 1?",
            reference_time_utc=datetime(2026, 6, 24, tzinfo=timezone.utc),
        )

        self.assertEqual(parsed.deadline_utc, datetime(2027, 6, 1, 23, 59, 59, tzinfo=timezone.utc))

    def test_parse_market_question_warns_for_missing_fields(self) -> None:
        parsed = parse_market_question(
            "Will ETH do something soon?",
            reference_time_utc=datetime(2026, 6, 24, tzinfo=timezone.utc),
        )

        self.assertEqual(parsed.asset, "unknown")
        self.assertIsNone(parsed.target_price)
        self.assertEqual(parsed.direction, "unknown")
        self.assertEqual(parsed.event_type, "unknown")
        self.assertIsNone(parsed.deadline_utc)
        self.assertEqual(parsed.confidence, 0.0)
        self.assertEqual(
            parsed.warnings,
            (
                "asset_not_detected",
                "target_price_not_detected",
                "direction_not_detected",
                "event_type_not_detected",
                "deadline_not_detected",
            ),
        )

    def test_parse_market_question_rejects_blank_question(self) -> None:
        with self.assertRaises(ValueError):
            parse_market_question(" ")

    def test_parse_market_question_handles_common_question_forms(self) -> None:
        reference = datetime(2026, 6, 24, tzinfo=timezone.utc)
        cases = [
            (
                "Will XBT exceed 125000 by Nov 15?",
                {
                    "target_price": 125000.0,
                    "direction": "above",
                    "event_type": "touch",
                    "deadline_utc": datetime(2026, 11, 15, 23, 59, 59, tzinfo=timezone.utc),
                },
            ),
            (
                "Will Bitcoin finish under 90k on Oct. 1, 2026?",
                {
                    "target_price": 90000.0,
                    "direction": "below",
                    "event_type": "terminal",
                    "deadline_utc": datetime(2026, 10, 1, 23, 59, 59, tzinfo=timezone.utc),
                },
            ),
            (
                "Will BTC be at least $110,000 on 12/31/2026?",
                {
                    "target_price": 110000.0,
                    "direction": "above",
                    "event_type": "terminal",
                    "deadline_utc": datetime(2026, 12, 31, 23, 59, 59, tzinfo=timezone.utc),
                },
            ),
            (
                "Will Bitcoin touch $95.5k before September 30th?",
                {
                    "target_price": 95500.0,
                    "direction": "unknown",
                    "event_type": "touch",
                    "deadline_utc": datetime(2026, 9, 30, 23, 59, 59, tzinfo=timezone.utc),
                },
            ),
            (
                "Will BTC close less than 75k on 1/15/27?",
                {
                    "target_price": 75000.0,
                    "direction": "below",
                    "event_type": "terminal",
                    "deadline_utc": datetime(2027, 1, 15, 23, 59, 59, tzinfo=timezone.utc),
                },
            ),
        ]

        for question, expected in cases:
            with self.subTest(question=question):
                parsed = parse_market_question(question, reference_time_utc=reference)
                self.assertEqual(parsed.asset, "BTC")
                self.assertEqual(parsed.target_price, expected["target_price"])
                self.assertEqual(parsed.direction, expected["direction"])
                self.assertEqual(parsed.event_type, expected["event_type"])
                self.assertEqual(parsed.deadline_utc, expected["deadline_utc"])


if __name__ == "__main__":
    unittest.main()
