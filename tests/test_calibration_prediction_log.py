import tempfile
import unittest
from datetime import datetime, timezone
from math import log
from pathlib import Path

from src.models import (
    HistoricalPrediction,
    calculate_brier_score,
    calculate_log_loss,
    check_realized_hit_rate_by_probability_bucket,
    generate_calibration_curve,
    read_historical_predictions,
    save_historical_prediction,
)


class HistoricalPredictionLogTests(unittest.TestCase):
    def test_save_and_read_historical_prediction(self) -> None:
        prediction = HistoricalPrediction(
            timestamp_utc=datetime(2026, 1, 1, 12, tzinfo=timezone.utc),
            market_id="btc-100k",
            question="Will Bitcoin hit $100,000 this week?",
            model_name="ensemble",
            probability=0.62,
            event_type="touch",
            deadline_utc=datetime(2026, 1, 5, tzinfo=timezone.utc),
            target_price=100000.0,
            direction="above",
            market_price=0.55,
            metadata={"source": "phase9-test"},
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "calibration" / "historical_predictions.jsonl"
            written = save_historical_prediction(path, prediction)
            rows = read_historical_predictions(path)

        self.assertEqual(written["market_id"], "btc-100k")
        self.assertEqual(rows, [written])
        self.assertEqual(rows[0]["probability"], 0.62)
        self.assertIsNone(rows[0]["outcome"])

    def test_build_from_prediction_recommendation_row(self) -> None:
        recommendation = {
            "timestamp_utc": "2026-01-01T12:00:00+00:00",
            "market_id": "btc-100k",
            "question": "Will Bitcoin hit $100,000 this week?",
            "model_name": "ensemble",
            "model_probability": 0.62,
        }

        prediction = HistoricalPrediction.from_recommendation(
            recommendation,
            event_type="touch",
            deadline_utc=datetime(2026, 1, 5, tzinfo=timezone.utc),
            target_price=100000.0,
            direction="above",
            market_price=0.55,
        )

        row = prediction.as_dict()
        self.assertEqual(row["probability"], 0.62)
        self.assertEqual(row["event_type"], "touch")
        self.assertEqual(row["direction"], "above")
        self.assertEqual(row["market_price"], 0.55)

    def test_read_missing_historical_prediction_log_returns_empty_list(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            rows = read_historical_predictions(Path(temp_dir) / "missing.jsonl")

        self.assertEqual(rows, [])

    def test_historical_prediction_rejects_invalid_values(self) -> None:
        base = {
            "timestamp_utc": "2026-01-01T12:00:00+00:00",
            "market_id": "btc-100k",
            "question": "Will Bitcoin hit $100,000 this week?",
            "model_name": "ensemble",
            "probability": 0.62,
            "event_type": "touch",
            "deadline_utc": None,
            "target_price": 100000.0,
            "direction": "above",
            "market_price": 0.55,
            "outcome": None,
            "resolved_at_utc": None,
            "metadata": {},
        }

        invalid_rows = (
            {**base, "probability": 1.1},
            {**base, "event_type": "settlement"},
            {**base, "direction": "sideways"},
            {**base, "target_price": 0.0},
            {**base, "metadata": []},
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "historical_predictions.jsonl"
            for row in invalid_rows:
                with self.subTest(row=row):
                    with self.assertRaises(ValueError):
                        save_historical_prediction(path, row)

    def test_calculate_brier_score_uses_resolved_predictions(self) -> None:
        base = {
            "timestamp_utc": "2026-01-01T12:00:00+00:00",
            "market_id": "btc-100k",
            "question": "Will Bitcoin hit $100,000 this week?",
            "model_name": "ensemble",
            "event_type": "touch",
            "deadline_utc": None,
            "target_price": 100000.0,
            "direction": "above",
            "market_price": 0.55,
            "resolved_at_utc": "2026-01-05T00:00:00+00:00",
            "metadata": {},
        }
        records = [
            {**base, "probability": 0.80, "outcome": 1.0},
            {**base, "market_id": "btc-90k", "probability": 0.25, "outcome": 0.0},
            {**base, "market_id": "btc-110k", "probability": 0.60, "outcome": None},
        ]

        result = calculate_brier_score(records)

        expected = (((0.80 - 1.0) ** 2) + ((0.25 - 0.0) ** 2)) / 2
        self.assertAlmostEqual(result.score, expected)
        self.assertEqual(result.resolved_count, 2)
        self.assertEqual(result.skipped_unresolved_count, 1)

    def test_calculate_brier_score_requires_resolved_prediction(self) -> None:
        record = HistoricalPrediction(
            timestamp_utc=datetime(2026, 1, 1, 12, tzinfo=timezone.utc),
            market_id="btc-100k",
            question="Will Bitcoin hit $100,000 this week?",
            model_name="ensemble",
            probability=0.62,
            event_type="touch",
        ).as_dict()

        with self.assertRaises(ValueError):
            calculate_brier_score([record])

    def test_calculate_log_loss_uses_resolved_predictions(self) -> None:
        base = {
            "timestamp_utc": "2026-01-01T12:00:00+00:00",
            "market_id": "btc-100k",
            "question": "Will Bitcoin hit $100,000 this week?",
            "model_name": "ensemble",
            "event_type": "touch",
            "deadline_utc": None,
            "target_price": 100000.0,
            "direction": "above",
            "market_price": 0.55,
            "resolved_at_utc": "2026-01-05T00:00:00+00:00",
            "metadata": {},
        }
        records = [
            {**base, "probability": 0.80, "outcome": 1.0},
            {**base, "market_id": "btc-90k", "probability": 0.25, "outcome": 0.0},
            {**base, "market_id": "btc-110k", "probability": 0.60, "outcome": None},
        ]

        result = calculate_log_loss(records)

        expected = ((-log(0.80)) + (-log(1.0 - 0.25))) / 2
        self.assertAlmostEqual(result.loss, expected)
        self.assertEqual(result.resolved_count, 2)
        self.assertEqual(result.skipped_unresolved_count, 1)
        self.assertEqual(result.clipped_probability_count, 0)

    def test_calculate_log_loss_clips_extreme_probabilities(self) -> None:
        base = HistoricalPrediction(
            timestamp_utc=datetime(2026, 1, 1, 12, tzinfo=timezone.utc),
            market_id="btc-100k",
            question="Will Bitcoin hit $100,000 this week?",
            model_name="ensemble",
            probability=1.0,
            event_type="touch",
            outcome=0.0,
        ).as_dict()

        result = calculate_log_loss([base], epsilon=0.01)

        self.assertAlmostEqual(result.loss, -log(0.01))
        self.assertEqual(result.clipped_probability_count, 1)

    def test_calculate_log_loss_requires_resolved_prediction(self) -> None:
        record = HistoricalPrediction(
            timestamp_utc=datetime(2026, 1, 1, 12, tzinfo=timezone.utc),
            market_id="btc-100k",
            question="Will Bitcoin hit $100,000 this week?",
            model_name="ensemble",
            probability=0.62,
            event_type="touch",
        ).as_dict()

        with self.assertRaises(ValueError):
            calculate_log_loss([record])

    def test_calculate_log_loss_rejects_invalid_epsilon(self) -> None:
        with self.assertRaises(ValueError):
            calculate_log_loss([], epsilon=0.5)

    def test_generate_calibration_curve_groups_resolved_predictions(self) -> None:
        base = {
            "timestamp_utc": "2026-01-01T12:00:00+00:00",
            "market_id": "btc-100k",
            "question": "Will Bitcoin hit $100,000 this week?",
            "model_name": "ensemble",
            "event_type": "touch",
            "deadline_utc": None,
            "target_price": 100000.0,
            "direction": "above",
            "market_price": 0.55,
            "resolved_at_utc": "2026-01-05T00:00:00+00:00",
            "metadata": {},
        }
        records = [
            {**base, "probability": 0.10, "outcome": 0.0},
            {**base, "market_id": "btc-2", "probability": 0.30, "outcome": 1.0},
            {**base, "market_id": "btc-3", "probability": 0.39, "outcome": 0.0},
            {**base, "market_id": "btc-4", "probability": 1.0, "outcome": 1.0},
            {**base, "market_id": "btc-5", "probability": 0.60, "outcome": None},
        ]

        result = generate_calibration_curve(records, bin_count=5)

        self.assertEqual(result.resolved_count, 4)
        self.assertEqual(result.skipped_unresolved_count, 1)
        self.assertEqual(len(result.buckets), 5)
        self.assertEqual(result.buckets[0].count, 1)
        self.assertEqual(result.buckets[1].count, 2)
        self.assertAlmostEqual(result.buckets[1].mean_predicted_probability, 0.345)
        self.assertAlmostEqual(result.buckets[1].observed_frequency, 0.5)
        self.assertEqual(result.buckets[4].count, 1)
        self.assertEqual(result.buckets[4].mean_predicted_probability, 1.0)
        self.assertEqual(result.buckets[4].observed_frequency, 1.0)

    def test_generate_calibration_curve_requires_resolved_prediction(self) -> None:
        record = HistoricalPrediction(
            timestamp_utc=datetime(2026, 1, 1, 12, tzinfo=timezone.utc),
            market_id="btc-100k",
            question="Will Bitcoin hit $100,000 this week?",
            model_name="ensemble",
            probability=0.62,
            event_type="touch",
        ).as_dict()

        with self.assertRaises(ValueError):
            generate_calibration_curve([record])

    def test_generate_calibration_curve_rejects_invalid_bin_count(self) -> None:
        with self.assertRaises(ValueError):
            generate_calibration_curve([], bin_count=0)

    def test_check_realized_hit_rate_by_probability_bucket_flags_gaps(self) -> None:
        base = {
            "timestamp_utc": "2026-01-01T12:00:00+00:00",
            "market_id": "btc-100k",
            "question": "Will Bitcoin hit $100,000 this week?",
            "model_name": "ensemble",
            "event_type": "touch",
            "deadline_utc": None,
            "target_price": 100000.0,
            "direction": "above",
            "market_price": 0.55,
            "resolved_at_utc": "2026-01-05T00:00:00+00:00",
            "metadata": {},
        }
        records = [
            {**base, "market_id": "good-1", "probability": 0.20, "outcome": 0.0},
            {**base, "market_id": "good-2", "probability": 0.25, "outcome": 0.0},
            {**base, "market_id": "good-3", "probability": 0.30, "outcome": 1.0},
            {**base, "market_id": "bad-1", "probability": 0.80, "outcome": 0.0},
            {**base, "market_id": "bad-2", "probability": 0.85, "outcome": 0.0},
            {**base, "market_id": "bad-3", "probability": 0.90, "outcome": 0.0},
            {**base, "market_id": "small-1", "probability": 0.55, "outcome": 1.0},
            {**base, "market_id": "pending", "probability": 0.55, "outcome": None},
        ]

        result = check_realized_hit_rate_by_probability_bucket(
            records,
            bin_count=3,
            min_bucket_count=3,
            max_abs_gap=0.20,
        )

        self.assertEqual(result.resolved_count, 7)
        self.assertEqual(result.skipped_unresolved_count, 1)
        self.assertEqual(result.checked_bucket_count, 2)
        self.assertEqual(result.insufficient_bucket_count, 1)
        self.assertEqual(result.flagged_bucket_count, 1)
        self.assertEqual(result.buckets[0].status, "calibrated")
        self.assertEqual(result.buckets[1].status, "insufficient_data")
        self.assertEqual(result.buckets[2].status, "miscalibrated")
        self.assertLess(result.buckets[2].calibration_gap, 0.0)

    def test_check_realized_hit_rate_by_probability_bucket_rejects_invalid_options(self) -> None:
        with self.assertRaises(ValueError):
            check_realized_hit_rate_by_probability_bucket([], min_bucket_count=0)
        with self.assertRaises(ValueError):
            check_realized_hit_rate_by_probability_bucket([], max_abs_gap=1.1)


if __name__ == "__main__":
    unittest.main()
