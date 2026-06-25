import unittest
from datetime import datetime, timezone

from src.paper import execute_paper_decision
from src.strategy import TradeDecision


class PaperExecutorTests(unittest.TestCase):
    def test_execute_paper_buy_yes_creates_open_paper_record(self) -> None:
        decision = TradeDecision(
            action="BUY_YES",
            model_probability=0.65,
            market_price=0.50,
            edge=0.15,
            expected_value=0.15,
            suggested_limit_price=0.50,
            position_size_usd=10.0,
            max_loss_usd=10.0,
            confidence=0.8,
            reasons=("paper_only_decision",),
            warnings=("model_uncertainty",),
        )
        execution = execute_paper_decision(
            decision=decision,
            market_id="btc-100k",
            question="Will Bitcoin hit $100,000 this week?",
            timestamp_utc=datetime(2026, 1, 1, 12, tzinfo=timezone.utc),
        )

        self.assertEqual(execution.status, "OPEN")
        self.assertEqual(execution.side, "YES")
        self.assertEqual(execution.entry_price, 0.50)
        self.assertEqual(execution.current_price, 0.50)
        self.assertEqual(execution.size_usd, 10.0)
        self.assertTrue(execution.paper_only)
        self.assertEqual(execution.mark_to_market_pnl, 0.0)
        row = execution.as_journal_row()
        self.assertEqual(row["action"], "BUY_YES")
        self.assertEqual(row["rationale"], ["paper_only_decision"])
        self.assertIsNone(row["final_resolution"])

    def test_execute_paper_hold_skips_position(self) -> None:
        decision = TradeDecision(
            action="HOLD",
            model_probability=0.51,
            market_price=None,
            edge=0.0,
            expected_value=0.0,
            suggested_limit_price=None,
            position_size_usd=0.0,
            max_loss_usd=0.0,
            confidence=0.5,
            reasons=("edge_below_threshold",),
        )
        execution = execute_paper_decision(
            decision=decision,
            market_id="btc-flat",
            question="Will Bitcoin be above $100,000?",
            timestamp_utc=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )

        self.assertEqual(execution.status, "SKIPPED")
        self.assertEqual(execution.side, "NONE")
        self.assertIsNone(execution.entry_price)
        self.assertEqual(execution.size_usd, 0.0)
        self.assertEqual(execution.rationale, ("edge_below_threshold",))

    def test_buy_decision_requires_positive_paper_size(self) -> None:
        decision = TradeDecision(
            action="BUY_NO",
            model_probability=0.35,
            market_price=0.50,
            edge=0.15,
            expected_value=0.15,
            suggested_limit_price=0.50,
            position_size_usd=0.0,
            max_loss_usd=0.0,
            confidence=0.8,
        )

        with self.assertRaises(ValueError):
            execute_paper_decision(
                decision=decision,
                market_id="btc-100k",
                question="Will Bitcoin hit $100,000 this week?",
                timestamp_utc=datetime(2026, 1, 1, tzinfo=timezone.utc),
            )


if __name__ == "__main__":
    unittest.main()
