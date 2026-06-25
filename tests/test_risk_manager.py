import unittest

from src.strategy import RiskDecision, apply_risk_limits


class RiskManagerTests(unittest.TestCase):
    def test_apply_risk_limits_approves_size_within_limits(self) -> None:
        decision = apply_risk_limits(bankroll_usd=1000.0, proposed_size_usd=5.0)

        self.assertIsInstance(decision, RiskDecision)
        self.assertTrue(decision.allowed)
        self.assertEqual(decision.approved_size_usd, 5.0)
        self.assertEqual(decision.max_loss_usd, 5.0)

    def test_apply_risk_limits_reduces_to_single_trade_cap(self) -> None:
        decision = apply_risk_limits(bankroll_usd=1000.0, proposed_size_usd=50.0)

        self.assertTrue(decision.allowed)
        self.assertEqual(decision.approved_size_usd, 10.0)
        self.assertIn("position_size_reduced_by_risk_limits", decision.warnings)

    def test_apply_risk_limits_blocks_loss_limits_unclear_rules_liquidity_and_spread(self) -> None:
        cases = [
            {"daily_pnl_usd": -30.0, "reason": "daily_loss_limit_reached"},
            {"weekly_pnl_usd": -80.0, "reason": "weekly_loss_limit_reached"},
            {"rules_clear": False, "reason": "rules_unclear"},
            {"liquidity_usd": 9.0, "min_liquidity_usd": 10.0, "reason": "low_liquidity"},
            {"spread": 0.11, "max_spread": 0.10, "reason": "wide_spread"},
        ]

        for case in cases:
            reason = case.pop("reason")
            with self.subTest(reason=reason):
                decision = apply_risk_limits(bankroll_usd=1000.0, proposed_size_usd=5.0, **case)
                self.assertFalse(decision.allowed)
                self.assertEqual(decision.approved_size_usd, 0.0)
                self.assertIn(reason, decision.reasons)

    def test_apply_risk_limits_blocks_when_btc_exposure_limit_is_reached(self) -> None:
        decision = apply_risk_limits(
            bankroll_usd=1000.0,
            proposed_size_usd=5.0,
            current_btc_exposure_usd=100.0,
        )

        self.assertFalse(decision.allowed)
        self.assertIn("btc_exposure_limit_reached", decision.reasons)

    def test_apply_risk_limits_rejects_invalid_inputs(self) -> None:
        invalid_cases = [
            {"bankroll_usd": 0.0, "proposed_size_usd": 1.0},
            {"bankroll_usd": 1000.0, "proposed_size_usd": -1.0},
            {"bankroll_usd": 1000.0, "proposed_size_usd": 1.0, "current_btc_exposure_usd": -1.0},
            {"bankroll_usd": 1000.0, "proposed_size_usd": 1.0, "max_single_trade_fraction": -0.01},
        ]

        for kwargs in invalid_cases:
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    apply_risk_limits(**kwargs)


if __name__ == "__main__":
    unittest.main()
