import unittest

from src.models import BootstrapFatTailResult, run_bootstrap_fat_tail_model


class BootstrapFatTailModelTests(unittest.TestCase):
    def test_run_bootstrap_fat_tail_model_is_reproducible_with_seed(self) -> None:
        kwargs = {
            "current_price": 100_000.0,
            "target_price": 105_000.0,
            "historical_log_returns": [-0.03, -0.01, 0.0, 0.02, 0.05],
            "days_to_expiry": 10.0,
            "n_paths": 2_000,
            "random_seed": 42,
            "mode": "terminal",
        }

        first = run_bootstrap_fat_tail_model(**kwargs)
        second = run_bootstrap_fat_tail_model(**kwargs)

        self.assertIsInstance(first, BootstrapFatTailResult)
        self.assertEqual(first, second)
        self.assertEqual(first.probability, first.terminal_probability)
        self.assertEqual(first.diagnostics["return_observations"], 5)

    def test_run_bootstrap_fat_tail_model_reports_touch_probability(self) -> None:
        result = run_bootstrap_fat_tail_model(
            current_price=100_000.0,
            target_price=110_000.0,
            historical_log_returns=[-0.02, 0.01, 0.03, 0.05],
            days_to_expiry=20.0,
            n_paths=2_000,
            random_seed=7,
            mode="touch",
        )

        self.assertEqual(result.probability, result.touch_probability)
        self.assertGreaterEqual(result.touch_probability, result.terminal_probability)
        self.assertGreaterEqual(result.expected_max_price, 100_000.0)
        self.assertLessEqual(result.expected_min_price, 100_000.0)

    def test_run_bootstrap_fat_tail_model_handles_below_target_direction(self) -> None:
        result = run_bootstrap_fat_tail_model(
            current_price=100_000.0,
            target_price=90_000.0,
            historical_log_returns=[-0.05, -0.02, 0.0, 0.01],
            days_to_expiry=15.0,
            n_paths=2_000,
            random_seed=9,
            mode="touch",
        )

        self.assertEqual(result.diagnostics["direction"], "below")
        self.assertGreaterEqual(result.touch_probability, result.terminal_probability)

    def test_run_bootstrap_fat_tail_model_rejects_invalid_inputs(self) -> None:
        valid = {
            "current_price": 100_000.0,
            "target_price": 110_000.0,
            "historical_log_returns": [-0.01, 0.02],
            "days_to_expiry": 30.0,
            "n_paths": 100,
        }
        invalid_cases = [
            {"current_price": 0.0},
            {"target_price": 0.0},
            {"historical_log_returns": [float("nan"), 0.01]},
            {"days_to_expiry": 0.0},
            {"n_paths": 0},
            {"mode": "bad"},
        ]

        for override in invalid_cases:
            with self.subTest(override=override):
                kwargs = dict(valid)
                kwargs.update(override)
                with self.assertRaises(ValueError):
                    run_bootstrap_fat_tail_model(**kwargs)


if __name__ == "__main__":
    unittest.main()
