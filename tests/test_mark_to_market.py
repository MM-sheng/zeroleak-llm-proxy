import unittest
from datetime import datetime, timezone

from src.paper import execute_paper_decision, mark_journal_row, mark_paper_execution
from src.strategy import TradeDecision


class MarkToMarketTests(unittest.TestCase):
    def test_mark_open_paper_execution_calculates_unrealized_pnl(self) -> None:
        execution = _open_execution(entry_price=0.50, size_usd=10.0)
        marked = mark_paper_execution(execution, current_price=0.60)

        self.assertEqual(marked.current_price, 0.60)
        self.assertAlmostEqual(marked.mark_to_market_pnl, 2.0)
        self.assertEqual(marked.status, "OPEN")
        self.assertTrue(marked.paper_only)

    def test_mark_hold_execution_remains_zero_pnl(self) -> None:
        decision = TradeDecision(
            action="HOLD",
            model_probability=0.50,
            market_price=None,
            edge=0.0,
            expected_value=0.0,
            suggested_limit_price=None,
            position_size_usd=0.0,
            max_loss_usd=0.0,
            confidence=0.5,
        )
        execution = execute_paper_decision(
            decision=decision,
            market_id="btc-flat",
            question="Will BTC be flat?",
            timestamp_utc=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
        marked = mark_paper_execution(execution, current_price=0.55)

        self.assertEqual(marked.current_price, 0.55)
        self.assertEqual(marked.mark_to_market_pnl, 0.0)
        self.assertEqual(marked.status, "SKIPPED")

    def test_mark_journal_row_updates_current_price_and_pnl(self) -> None:
        row = _open_execution(entry_price=0.40, size_usd=20.0).as_journal_row()
        marked = mark_journal_row(row, current_price=0.30)

        self.assertEqual(marked["current_price"], 0.30)
        self.assertAlmostEqual(marked["mark_to_market_pnl"], -5.0)

    def test_mark_to_market_rejects_invalid_current_price(self) -> None:
        execution = _open_execution(entry_price=0.50, size_usd=10.0)

        with self.assertRaises(ValueError):
            mark_paper_execution(execution, current_price=1.1)


def _open_execution(*, entry_price: float, size_usd: float):
    decision = TradeDecision(
        action="BUY_YES",
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
