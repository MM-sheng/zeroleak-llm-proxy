import unittest

from src.models import MonteCarloGBMResult, run_monte_carlo_gbm


class MonteCarloGBMModelTests(unittest.TestCase):
    def test_run_monte_carlo_gbm_is_reproducible_with_seed(self) -> None:
        kwargs = {
            "current_price": 100_000.0,
            "target_price": 110_000.0,
            "days_to_expiry": 30.0,
            "annualized_volatility": 0.60,
            "drift": 0.0,
            "n_paths": 2_000,
            "random_seed": 42,
            "mode": "terminal",
        }

        first = run_monte_carlo_gbm(**kwargs)
        second = run_monte_carlo_gbm(**kwargs)

        self.assertIsInstance(first, MonteCarloGBMResult)
        self.assertEqual(first, second)
        self.assertEqual(first.probability, first.terminal_probability)
        self.assertEqual(first.diagnostics["direction"], "above")
        self.assertEqual(first.diagnostics["steps"], 30)

    def test_run_monte_carlo_gbm_reports_touch_probability_for_touch_mode(self) -> None:
        result = run_monte_carlo_gbm(
            current_price=100_000.0,
            target_price=110_000.0,
            days_to_expiry=30.0,
            annualized_volatility=0.60,
            n_paths=2_000,
            random_seed=7,
            mode="touch",
        )

        self.assertEqual(result.probability, result.touch_probability)
        self.assertGreaterEqual(result.touch_probability, result.terminal_probability)
        self.assertGreaterEqual(result.expected_max_price, 100_000.0)
        self.assertLessEqual(result.expected_min_price, 100_000.0)
        for value in [result.probability, result.terminal_probability, result.touch_probability]:
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)

    def test_run_monte_carlo_gbm_handles_below_target_direction(self) -> None:
        result = run_monte_carlo_gbm(
            current_price=100_000.0,
            target_price=90_000.0,
            days_to_expiry=20.0,
            annualized_volatility=0.50,
            n_paths=2_000,
            random_seed=9,
            mode="touch",
        )

        self.assertEqual(result.diagnostics["direction"], "below")
        self.assertGreaterEqual(result.touch_probability, result.terminal_probability)

    def test_run_monte_carlo_gbm_zero_volatility_is_deterministic(self) -> None:
        result = run_monte_carlo_gbm(
            current_price=100_000.0,
            target_price=110_000.0,
            days_to_expiry=10.0,
            annualized_volatility=0.0,
            drift=0.0,
            n_paths=100,
            random_seed=1,
            mode="touch",
        )

        self.assertEqual(result.probability, 0.0)
        self.assertEqual(result.terminal_probability, 0.0)
        self.assertEqual(result.touch_probability, 0.0)
        self.assertEqual(result.quantiles["terminal_p50"], 100_000.0)

    def test_run_monte_carlo_gbm_rejects_invalid_inputs(self) -> None:
        valid = {
            "current_price": 100_000.0,
            "target_price": 110_000.0,
            "days_to_expiry": 30.0,
            "annualized_volatility": 0.60,
            "n_paths": 100,
        }
        invalid_cases = [
            {"current_price": 0.0},
            {"target_price": 0.0},
            {"days_to_expiry": 0.0},
            {"annualized_volatility": -0.01},
            {"n_paths": 0},
            {"mode": "bad"},
        ]

        for override in invalid_cases:
            with self.subTest(override=override):
                kwargs = dict(valid)
                kwargs.update(override)
                with self.assertRaises(ValueError):
                    run_monte_carlo_gbm(**kwargs)


if __name__ == "__main__":
    unittest.main()
