import io
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from src.main import build_daily_report_from_journal, main
from src.paper import append_journal_entry, execute_paper_decision
from src.strategy import TradeDecision


class MainReportCliTests(unittest.TestCase):
    def test_build_daily_report_from_missing_journal_is_empty_report(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            report = build_daily_report_from_journal(
                journal_path=Path(temp_dir) / "missing.jsonl",
                generated_at_utc=datetime(2026, 1, 1, tzinfo=timezone.utc),
                spot_price_usd=100000.0,
            )

        self.assertEqual(report.btc_current_state["spot_price_usd"], "$100,000.00 USD")
        self.assertEqual(report.markets, ())
        self.assertEqual(report.best_opportunity, "No paper opportunity selected.")

    def test_main_report_writes_markdown_from_journal(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            journal_path = root / "paper" / "journal.jsonl"
            output_path = root / "reports" / "daily_report.md"
            append_journal_entry(journal_path, _execution())
            output = io.StringIO()

            exit_code = main(
                [
                    "report",
                    "--journal",
                    str(journal_path),
                    "--output",
                    str(output_path),
                    "--spot-price-usd",
                    "100000",
                ],
                out=output,
            )
            markdown = output_path.read_text(encoding="utf-8")

        self.assertEqual(exit_code, 0)
        self.assertIn("wrote paper-only report:", output.getvalue())
        self.assertIn("BTC Polymarket Daily Paper Report", markdown)
        self.assertIn("paper-only research", markdown)
        self.assertIn("btc-100k", markdown)
        self.assertIn("$100,000.00 USD", markdown)


def _execution():
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
    )
    return execute_paper_decision(
        decision=decision,
        market_id="btc-100k",
        question="Will Bitcoin hit $100,000 this week?",
        timestamp_utc=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )


if __name__ == "__main__":
    unittest.main()
