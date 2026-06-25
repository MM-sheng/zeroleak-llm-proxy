import unittest

from src.models import (
    ModelDiagnostics,
    ModelProbability,
    build_model_diagnostics,
    combine_model_probabilities,
    diagnostics_from_result,
)


class ModelDiagnosticsTests(unittest.TestCase):
    def test_build_model_diagnostics_normalizes_to_serializable_dict(self) -> None:
        diagnostics = build_model_diagnostics(
            model_name=" gbm ",
            probability="0.42",
            diagnostics={"n_paths": 1000},
            warnings=["wide_uncertainty"],
        )

        self.assertIsInstance(diagnostics, ModelDiagnostics)
        self.assertEqual(diagnostics.model_name, "gbm")
        self.assertEqual(diagnostics.probability, 0.42)
        self.assertEqual(diagnostics.warnings, ("wide_uncertainty",))
        self.assertEqual(
            diagnostics.as_dict(),
            {
                "model_name": "gbm",
                "probability": 0.42,
                "diagnostics": {"n_paths": 1000},
                "warnings": ["wide_uncertainty"],
                "summary": "gbm: probability=0.4200",
            },
        )

    def test_diagnostics_from_result_reads_common_result_attributes(self) -> None:
        result = combine_model_probabilities(
            [
                ModelProbability(name="gbm", probability=0.60),
                ModelProbability(name="bootstrap", probability=0.40),
            ]
        )

        diagnostics = diagnostics_from_result("ensemble", result)

        self.assertEqual(diagnostics.model_name, "ensemble")
        self.assertEqual(diagnostics.probability, 0.50)
        self.assertEqual(diagnostics.diagnostics["component_count"], 2)

    def test_build_model_diagnostics_rejects_invalid_inputs(self) -> None:
        invalid_cases = [
            {"model_name": "", "probability": 0.5},
            {"model_name": "bad", "probability": -0.01},
            {"model_name": "bad", "probability": 1.01},
        ]

        for kwargs in invalid_cases:
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    build_model_diagnostics(**kwargs)

    def test_diagnostics_from_result_rejects_missing_probability(self) -> None:
        with self.assertRaises(ValueError):
            diagnostics_from_result("bad", object())


if __name__ == "__main__":
    unittest.main()
