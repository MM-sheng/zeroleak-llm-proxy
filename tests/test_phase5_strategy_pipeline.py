import unittest

from src.strategy import (
    calculate_edges,
    calculate_expected_value,
    calculate_kelly_sizing,
    apply_risk_limits,
    make_trade_decision,
)


class Phase5StrategyPipelineTests(unittest.TestCase):
    def test_phase5_strategy_pipeline_stays_paper_only_and_consistent(self) -> None:
        edge = calculate_edges(model_probability=0.65, yes_price=0.50, no_price=0.48)
        ev = calculate_expected_value(model_probability=0.65, yes_price=0.50, no_price=0.48)
        sizing = calculate_kelly_sizing(probability=0.65, price=0.50, bankroll_usd=1000.0)
        risk = apply_risk_limits(bankroll_usd=1000.0, proposed_size_usd=sizing.position_size_usd)
        decision = make_trade_decision(
            model_probability=0.65,
            yes_price=0.50,
            no_price=0.48,
            bankroll_usd=1000.0,
        )

        self.assertEqual(edge.best_side, "YES")
        self.assertEqual(ev.best_side, "YES")
        self.assertTrue(risk.allowed)
        self.assertEqual(decision.action, "BUY_YES")
        self.assertEqual(decision.position_size_usd, risk.approved_size_usd)
        self.assertIn("paper_only_decision", decision.reasons)

    def test_phase5_strategy_pipeline_holds_when_risk_blocks(self) -> None:
        decision = make_trade_decision(
            model_probability=0.65,
            yes_price=0.50,
            no_price=0.48,
            bankroll_usd=1000.0,
            rules_clear=False,
        )

        self.assertEqual(decision.action, "HOLD")
        self.assertIn("rules_unclear", decision.reasons)
        self.assertEqual(decision.position_size_usd, 0.0)


if __name__ == "__main__":
    unittest.main()
