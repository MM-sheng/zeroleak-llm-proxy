import unittest

from src.models import (
    EnsembleProbabilityResult,
    ModelProbability,
    combine_model_probabilities,
)


class EnsembleModelTests(unittest.TestCase):
    def test_combine_model_probabilities_uses_normalized_weights(self) -> None:
        result = combine_model_probabilities(
            [
                ModelProbability(name="gbm", probability=0.60, weight=2.0),
                ModelProbability(name="bootstrap", probability=0.30, weight=1.0),
            ]
        )

        self.assertIsInstance(result, EnsembleProbabilityResult)
        self.assertAlmostEqual(result.probability, 0.50)
        self.assertAlmostEqual(result.normalized_weights["gbm"], 2 / 3)
        self.assertAlmostEqual(result.normalized_weights["bootstrap"], 1 / 3)
        self.assertEqual(result.diagnostics["component_count"], 2)

    def test_combine_model_probabilities_flags_model_disagreement(self) -> None:
        result = combine_model_probabilities(
            [
                ModelProbability(name="low", probability=0.10),
                ModelProbability(name="high", probability=0.90),
            ],
            disagreement_threshold=0.25,
        )

        self.assertIn("model_disagreement", result.warnings)
        self.assertEqual(result.diagnostics["dispersion"], 0.80)

    def test_combine_model_probabilities_preserves_component_warnings(self) -> None:
        result = combine_model_probabilities(
            [
                ModelProbability(name="gbm", probability=0.50, warnings=("wide_uncertainty",)),
                ModelProbability(name="bootstrap", probability=0.55),
            ]
        )

        self.assertIn("wide_uncertainty", result.warnings)

    def test_model_probability_rejects_invalid_inputs(self) -> None:
        invalid_cases = [
            {"name": "", "probability": 0.5},
            {"name": "bad", "probability": -0.01},
            {"name": "bad", "probability": 1.01},
            {"name": "bad", "probability": 0.5, "weight": 0},
        ]

        for kwargs in invalid_cases:
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    ModelProbability(**kwargs)

    def test_combine_model_probabilities_rejects_invalid_inputs(self) -> None:
        with self.assertRaises(ValueError):
            combine_model_probabilities([])
        with self.assertRaises(ValueError):
            combine_model_probabilities([ModelProbability(name="gbm", probability=0.5)], disagreement_threshold=-1)


if __name__ == "__main__":
    unittest.main()
