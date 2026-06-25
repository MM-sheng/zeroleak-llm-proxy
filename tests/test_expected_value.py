import unittest

from src.strategy import ExpectedValueResult, calculate_expected_value


class ExpectedValueTests(unittest.TestCase):
    def test_calculate_expected_value_computes_yes_and_no_ev(self) -> None:
        result = calculate_expected_value(model_probability=0.62, yes_price=0.55, no_price=0.43)

        self.assertIsInstance(result, ExpectedValueResult)
        self.assertAlmostEqual(result.ev_yes, 0.62 * 0.45 - 0.38 * 0.55)
        self.assertAlmostEqual(result.ev_no, 0.38 * 0.57 - 0.62 * 0.43)
        self.assertEqual(result.best_side, "YES")
        self.assertAlmostEqual(result.best_ev, result.ev_yes)

    def test_calculate_expected_value_can_select_no_side(self) -> None:
        result = calculate_expected_value(model_probability=0.40, yes_price=0.45, no_price=0.52)

        self.assertEqual(result.best_side, "NO")
        self.assertAlmostEqual(result.best_ev, result.ev_no)

    def test_calculate_expected_value_returns_none_when_both_ev_are_non_positive(self) -> None:
        result = calculate_expected_value(model_probability=0.50, yes_price=0.55, no_price=0.55)

        self.assertEqual(result.best_side, "NONE")
        self.assertAlmostEqual(result.best_ev, -0.05)
        self.assertIn("wide_or_inconsistent_prices", result.warnings)

    def test_calculate_expected_value_rejects_invalid_probabilities(self) -> None:
        invalid_cases = [
            {"model_probability": -0.01, "yes_price": 0.5, "no_price": 0.5},
            {"model_probability": 1.01, "yes_price": 0.5, "no_price": 0.5},
            {"model_probability": 0.5, "yes_price": -0.01, "no_price": 0.5},
            {"model_probability": 0.5, "yes_price": 0.5, "no_price": 1.01},
        ]

        for kwargs in invalid_cases:
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    calculate_expected_value(**kwargs)


if __name__ == "__main__":
    unittest.main()
