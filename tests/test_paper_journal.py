import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from src.paper import JOURNAL_FIELDS, append_journal_entry, read_journal
from src.paper.paper_executor import execute_paper_decision
from src.strategy import TradeDecision


class PaperTradeJournalTests(unittest.TestCase):
    def test_append_and_read_paper_execution_jsonl(self) -> None:
        decision = TradeDecision(
            action="BUY_NO",
            model_probability=0.35,
            market_price=0.40,
            edge=0.25,
            expected_value=0.25,
            suggested_limit_price=0.40,
            position_size_usd=8.0,
            max_loss_usd=8.0,
            confidence=0.7,
            reasons=("paper_only_decision",),
        )
        execution = execute_paper_decision(
            decision=decision,
            market_id="btc-no-100k",
            question="Will Bitcoin fail to hit $100,000 this week?",
            timestamp_utc=datetime(2026, 1, 1, 1, tzinfo=timezone.utc),
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            journal_path = Path(temp_dir) / "paper" / "journal.jsonl"
            written = append_journal_entry(journal_path, execution)
            rows = read_journal(journal_path)

        self.assertEqual(tuple(written.keys()), JOURNAL_FIELDS)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["market_id"], "btc-no-100k")
        self.assertEqual(rows[0]["action"], "BUY_NO")
        self.assertEqual(rows[0]["side"], "NO")
        self.assertEqual(rows[0]["size_usd"], 8.0)
        self.assertEqual(rows[0]["rationale"], ["paper_only_decision"])

    def test_read_missing_journal_returns_empty_list(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            rows = read_journal(Path(temp_dir) / "missing.jsonl")

        self.assertEqual(rows, [])

    def test_journal_rejects_missing_required_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaises(ValueError):
                append_journal_entry(Path(temp_dir) / "journal.jsonl", {"market_id": "btc"})


if __name__ == "__main__":
    unittest.main()
