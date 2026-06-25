import unittest
from datetime import datetime, timezone

from src.paper import execute_paper_decision, resolve_journal_row, resolve_paper_execution
from src.strategy import TradeDecision


class ManualResolutionTests(unittest.TestCase):
    def test_resolve_winning_yes_execution_calculates_realized_pnl(self) -> None:
        execution = _execution(action="BUY_YES", entry_price=0.50, size_usd=10.0)
        resolved = resolve_paper_execution(execution, final_resolution="YES", lesson="rules matched")

        self.assertEqual(resolved.final_resolution, "YES")
        self.assertEqual(resolved.current_price, 1.0)
        self.assertAlmostEqual(resolved.realized_pnl, 10.0)
        self.assertAlmostEqual(resolved.mark_to_market_pnl, 10.0)
        self.assertEqual(resolved.lesson, "rules matched")

    def test_resolve_losing_no_journal_row_calculates_loss(self) -> None:
        row = _execution(action="BUY_NO", entry_price=0.25, size_usd=5.0).as_journal_row()
        resolved = resolve_journal_row(row, final_resolution="YES", lesson="manual review")

        self.assertEqual(resolved["final_resolution"], "YES")
        self.assertEqual(resolved["current_price"], 0.0)
        self.assertAlmostEqual(resolved["realized_pnl"], -5.0)
        self.assertEqual(resolved["lesson"], "manual review")

    def test_void_and_hold_resolutions_have_zero_realized_pnl(self) -> None:
        execution = _execution(action="BUY_YES", entry_price=0.50, size_usd=10.0)
        voided = resolve_paper_execution(execution, final_resolution="VOID")
        self.assertEqual(voided.realized_pnl, 0.0)
        self.assertIsNone(voided.current_price)

        hold = execute_paper_decision(
            decision=TradeDecision(
                action="HOLD",
                model_probability=0.50,
                market_price=None,
                edge=0.0,
                expected_value=0.0,
                suggested_limit_price=None,
                position_size_usd=0.0,
                max_loss_usd=0.0,
                confidence=0.5,
            ),
            market_id="btc-hold",
            question="Will BTC hold?",
            timestamp_utc=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
        resolved_hold = resolve_paper_execution(hold, final_resolution="YES")
        self.assertEqual(resolved_hold.realized_pnl, 0.0)
        self.assertIsNone(resolved_hold.current_price)

    def test_manual_resolution_rejects_invalid_resolution(self) -> None:
        execution = _execution(action="BUY_YES", entry_price=0.50, size_usd=10.0)

        with self.assertRaises(ValueError):
            resolve_paper_execution(execution, final_resolution="MAYBE")  # type: ignore[arg-type]


def _execution(*, action: str, entry_price: float, size_usd: float):
    decision = TradeDecision(
        action=action,  # type: ignore[arg-type]
        model_probability=0.65,
        market_price=entry_price,
        edge=0.15,
        expected_value=0.15,
        suggested_limit_price=entry_price,
        position_size_usd=size_usd,
        max_loss_usd=size_usd,
        confidence=0.8,
        reasons=("paper_only_decision",),
    )
    return execute_paper_decision(
        decision=decision,
        market_id="btc-100k",
        question="Will Bitcoin hit $100,000 this week?",
        timestamp_utc=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )


if __name__ == "__main__":
    unittest.main()
