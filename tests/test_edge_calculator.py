import unittest

from src.strategy import EdgeResult, calculate_edges


class EdgeCalculatorTests(unittest.TestCase):
    def test_calculate_edges_computes_yes_and_no_edge(self) -> None:
        result = calculate_edges(model_probability=0.62, yes_price=0.55, no_price=0.43)

        self.assertIsInstance(result, EdgeResult)
        self.assertAlmostEqual(result.edge_yes, 0.07)
        self.assertAlmostEqual(result.edge_no, -0.05)
        self.assertEqual(result.best_side, "YES")
        self.assertAlmostEqual(result.best_edge, 0.07)

    def test_calculate_edges_can_select_no_side(self) -> None:
        result = calculate_edges(model_probability=0.40, yes_price=0.45, no_price=0.52)

        self.assertAlmostEqual(result.edge_yes, -0.05)
        self.assertAlmostEqual(result.edge_no, 0.08)
        self.assertEqual(result.best_side, "NO")
        self.assertAlmostEqual(result.best_edge, 0.08)

    def test_calculate_edges_returns_none_when_both_edges_are_non_positive(self) -> None:
        result = calculate_edges(model_probability=0.50, yes_price=0.55, no_price=0.55)

        self.assertEqual(result.best_side, "NONE")
        self.assertAlmostEqual(result.best_edge, -0.05)
        self.assertIn("wide_or_inconsistent_prices", result.warnings)

    def test_calculate_edges_rejects_invalid_probabilities(self) -> None:
        invalid_cases = [
            {"model_probability": -0.01, "yes_price": 0.5, "no_price": 0.5},
            {"model_probability": 1.01, "yes_price": 0.5, "no_price": 0.5},
            {"model_probability": 0.5, "yes_price": -0.01, "no_price": 0.5},
            {"model_probability": 0.5, "yes_price": 0.5, "no_price": 1.01},
        ]

        for kwargs in invalid_cases:
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    calculate_edges(**kwargs)


if __name__ == "__main__":
    unittest.main()
