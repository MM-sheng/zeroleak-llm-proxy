import unittest

from src.strategy import TradeDecision, make_trade_decision


class TradeDecisionTests(unittest.TestCase):
    def test_make_trade_decision_can_buy_yes_on_positive_edge_ev_and_risk(self) -> None:
        decision = make_trade_decision(
            model_probability=0.65,
            yes_price=0.50,
            no_price=0.48,
            bankroll_usd=1000.0,
            confidence=0.8,
        )

        self.assertIsInstance(decision, TradeDecision)
        self.assertEqual(decision.action, "BUY_YES")
        self.assertEqual(decision.market_price, 0.50)
        self.assertGreater(decision.edge, 0.0)
        self.assertGreater(decision.expected_value, 0.0)
        self.assertGreater(decision.position_size_usd, 0.0)
        self.assertIn("paper_only_decision", decision.reasons)

    def test_make_trade_decision_can_buy_no(self) -> None:
        decision = make_trade_decision(
            model_probability=0.35,
            yes_price=0.40,
            no_price=0.50,
            bankroll_usd=1000.0,
        )

        self.assertEqual(decision.action, "BUY_NO")
        self.assertEqual(decision.market_price, 0.50)
        self.assertGreater(decision.position_size_usd, 0.0)

    def test_make_trade_decision_blocks_buy_when_calibration_is_poor(self) -> None:
        decision = make_trade_decision(
            model_probability=0.65,
            yes_price=0.50,
            no_price=0.48,
            bankroll_usd=1000.0,
            calibration_is_poor=True,
        )

        self.assertEqual(decision.action, "HOLD")
        self.assertIn("poor_calibration", decision.reasons)
        self.assertIn("calibration_blocked_buy_signal", decision.warnings)
        self.assertEqual(decision.position_size_usd, 0.0)

    def test_make_trade_decision_blocks_buy_no_when_calibration_is_poor(self) -> None:
        decision = make_trade_decision(
            model_probability=0.35,
            yes_price=0.40,
            no_price=0.50,
            bankroll_usd=1000.0,
            calibration_is_poor=True,
        )

        self.assertEqual(decision.action, "HOLD")
        self.assertIn("poor_calibration", decision.reasons)

    def test_make_trade_decision_holds_when_edge_or_ev_is_not_positive(self) -> None:
        decision = make_trade_decision(
            model_probability=0.50,
            yes_price=0.55,
            no_price=0.55,
            bankroll_usd=1000.0,
        )

        self.assertEqual(decision.action, "HOLD")
        self.assertIn("edge_below_threshold", decision.reasons)
        self.assertIn("expected_value_below_threshold", decision.reasons)
        self.assertEqual(decision.position_size_usd, 0.0)

    def test_make_trade_decision_holds_when_risk_blocks(self) -> None:
        decision = make_trade_decision(
            model_probability=0.65,
            yes_price=0.50,
            no_price=0.48,
            bankroll_usd=1000.0,
            daily_pnl_usd=-30.0,
        )

        self.assertEqual(decision.action, "HOLD")
        self.assertIn("daily_loss_limit_reached", decision.reasons)

    def test_make_trade_decision_rejects_invalid_confidence(self) -> None:
        with self.assertRaises(ValueError):
            make_trade_decision(
                model_probability=0.65,
                yes_price=0.50,
                no_price=0.48,
                bankroll_usd=1000.0,
                confidence=1.01,
            )


if __name__ == "__main__":
    unittest.main()
