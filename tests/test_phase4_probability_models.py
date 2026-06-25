import unittest

import numpy as np
import pandas as pd

from src.models import (
    ModelProbability,
    combine_model_probabilities,
    diagnostics_from_result,
    estimate_historical_volatility,
    run_bootstrap_fat_tail_model,
    run_monte_carlo_gbm,
)


class Phase4ProbabilityModelsTests(unittest.TestCase):
    def test_phase4_probability_pipeline_runs_offline_with_deterministic_models(self) -> None:
        closes = pd.Series([100000.0, 101000.0, 99000.0, 102000.0, 104000.0, 103000.0])
        price_data = pd.DataFrame(
            {
                "timestamp_utc": pd.to_datetime(
                    ["2026-01-01", "2026-01-02", "2026-01-03", "2026-01-04", "2026-01-05", "2026-01-06"],
                    utc=True,
                ),
                "close": closes,
            }
        )

        volatility = estimate_historical_volatility(price_data, window=5, periods_per_year=365)
        historical_returns = np.log(closes / closes.shift(1)).dropna()
        gbm = run_monte_carlo_gbm(
            current_price=volatility.latest_close,
            target_price=110000.0,
            days_to_expiry=14.0,
            annualized_volatility=volatility.annualized_volatility,
            drift=volatility.annualized_mean_log_return,
            n_paths=1000,
            random_seed=11,
            mode="touch",
        )
        bootstrap = run_bootstrap_fat_tail_model(
            current_price=volatility.latest_close,
            target_price=110000.0,
            historical_log_returns=historical_returns,
            days_to_expiry=14.0,
            n_paths=1000,
            random_seed=11,
            mode="touch",
        )
        ensemble = combine_model_probabilities(
            [
                ModelProbability(name="gbm", probability=gbm.probability, weight=0.5),
                ModelProbability(name="bootstrap", probability=bootstrap.probability, weight=0.5),
            ]
        )
        diagnostics = diagnostics_from_result("ensemble", ensemble)

        self.assertGreaterEqual(ensemble.probability, 0.0)
        self.assertLessEqual(ensemble.probability, 1.0)
        self.assertEqual(diagnostics.model_name, "ensemble")
        self.assertEqual(diagnostics.diagnostics["component_count"], 2)
        self.assertEqual(set(ensemble.normalized_weights), {"gbm", "bootstrap"})


if __name__ == "__main__":
    unittest.main()
