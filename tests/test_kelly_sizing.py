import unittest

from src.strategy import KellySizingResult, calculate_kelly_sizing


class KellySizingTests(unittest.TestCase):
    def test_calculate_kelly_sizing_uses_quarter_kelly(self) -> None:
        result = calculate_kelly_sizing(probability=0.60, price=0.50, bankroll_usd=1000.0)

        self.assertIsInstance(result, KellySizingResult)
        self.assertAlmostEqual(result.base_kelly_fraction, 0.20)
        self.assertAlmostEqual(result.quarter_kelly_fraction, 0.05)
        self.assertAlmostEqual(result.position_size_usd, 50.0)
        self.assertAlmostEqual(result.max_loss_usd, 50.0)
        self.assertEqual(result.warnings, ())

    def test_calculate_kelly_sizing_clips_non_positive_kelly_to_zero(self) -> None:
        result = calculate_kelly_sizing(probability=0.45, price=0.50, bankroll_usd=1000.0)

        self.assertEqual(result.base_kelly_fraction, 0.0)
        self.assertEqual(result.quarter_kelly_fraction, 0.0)
        self.assertEqual(result.position_size_usd, 0.0)
        self.assertIn("non_positive_kelly", result.warnings)

    def test_calculate_kelly_sizing_rejects_invalid_inputs(self) -> None:
        invalid_cases = [
            {"probability": -0.01, "price": 0.5, "bankroll_usd": 1000.0},
            {"probability": 1.01, "price": 0.5, "bankroll_usd": 1000.0},
            {"probability": 0.5, "price": -0.01, "bankroll_usd": 1000.0},
            {"probability": 0.5, "price": 1.0, "bankroll_usd": 1000.0},
            {"probability": 0.5, "price": 0.5, "bankroll_usd": 0.0},
        ]

        for kwargs in invalid_cases:
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    calculate_kelly_sizing(**kwargs)


if __name__ == "__main__":
    unittest.main()
