import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from src.paper import (
    RECOMMENDATION_FIELDS,
    PredictionRecommendation,
    read_prediction_recommendations,
    save_prediction_recommendation,
)
from src.strategy import TradeDecision


class RecommendationLogTests(unittest.TestCase):
    def test_save_and_read_prediction_recommendation_from_trade_decision(self) -> None:
        decision = TradeDecision(
            action="BUY_YES",
            model_probability=0.64,
            market_price=0.50,
            edge=0.14,
            expected_value=0.14,
            suggested_limit_price=0.50,
            position_size_usd=9.0,
            max_loss_usd=9.0,
            confidence=0.7,
            reasons=("paper_only_decision",),
            warnings=("wide_uncertainty",),
        )
        record = PredictionRecommendation.from_trade_decision(
            decision=decision,
            market_id="btc-100k",
            question="Will Bitcoin hit $100,000 this week?",
            model_name="ensemble",
            timestamp_utc=datetime(2026, 1, 1, 9, tzinfo=timezone.utc),
            model_diagnostics={"component_count": 2},
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "recommendations.jsonl"
            written = save_prediction_recommendation(path, record)
            rows = read_prediction_recommendations(path)

        self.assertEqual(tuple(written.keys()), RECOMMENDATION_FIELDS)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["market_id"], "btc-100k")
        self.assertEqual(rows[0]["model_name"], "ensemble")
        self.assertEqual(rows[0]["model_probability"], 0.64)
        self.assertEqual(rows[0]["action"], "BUY_YES")
        self.assertEqual(rows[0]["reasons"], ["paper_only_decision"])
        self.assertEqual(rows[0]["warnings"], ["wide_uncertainty"])

    def test_read_missing_recommendation_log_returns_empty_list(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            rows = read_prediction_recommendations(Path(temp_dir) / "missing.jsonl")

        self.assertEqual(rows, [])

    def test_recommendation_rejects_invalid_probability(self) -> None:
        row = {
            "timestamp_utc": "2026-01-01T00:00:00+00:00",
            "market_id": "btc",
            "question": "Will BTC rise?",
            "model_name": "ensemble",
            "model_probability": 1.5,
            "model_diagnostics": {},
            "action": "HOLD",
            "edge": 0.0,
            "expected_value": 0.0,
            "suggested_limit_price": None,
            "position_size_usd": 0.0,
            "reasons": [],
            "warnings": [],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaises(ValueError):
                save_prediction_recommendation(Path(temp_dir) / "recommendations.jsonl", row)


if __name__ == "__main__":
    unittest.main()
