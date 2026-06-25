import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from src.paper import (
    PredictionRecommendation,
    append_journal_entry,
    execute_paper_decision,
    mark_journal_row,
    read_journal,
    read_prediction_recommendations,
    resolve_journal_row,
    save_prediction_recommendation,
)
from src.reports import DailyReport, DailyReportMarket, write_daily_report
from src.strategy import make_trade_decision


class Phase7PaperPipelineTests(unittest.TestCase):
    def test_phase7_paper_pipeline_runs_offline(self) -> None:
        timestamp = datetime(2026, 1, 1, 10, tzinfo=timezone.utc)
        decision = make_trade_decision(
            model_probability=0.65,
            yes_price=0.50,
            no_price=0.48,
            bankroll_usd=1000.0,
        )
        execution = execute_paper_decision(
            decision=decision,
            market_id="btc-100k",
            question="Will Bitcoin hit $100,000 this week?",
            timestamp_utc=timestamp,
        )
        recommendation = PredictionRecommendation.from_trade_decision(
            decision=decision,
            market_id=execution.market_id,
            question=execution.question,
            model_name="ensemble",
            timestamp_utc=timestamp,
            model_diagnostics={"component_count": 2},
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            journal_path = root / "paper" / "journal.jsonl"
            recommendations_path = root / "paper" / "recommendations.jsonl"
            report_path = root / "reports" / "daily_report.md"

            append_journal_entry(journal_path, execution)
            save_prediction_recommendation(recommendations_path, recommendation)
            marked_row = mark_journal_row(read_journal(journal_path)[0], current_price=0.60)
            resolved_row = resolve_journal_row(marked_row, final_resolution="YES", lesson="paper pipeline test")
            report_markdown = write_daily_report(
                report_path,
                DailyReport(
                    generated_at_utc=timestamp,
                    btc_current_state={"spot_price_usd": "$100,000 USD"},
                    markets=(
                        DailyReportMarket(
                            market_id=execution.market_id,
                            question=execution.question,
                            yes_price=0.50,
                            no_price=0.48,
                            model_probability=decision.model_probability,
                            edge=decision.edge,
                            action=decision.action,
                            suggested_limit_price=decision.suggested_limit_price,
                            suggested_position_usd=decision.position_size_usd,
                            reasons_not_to_trade=decision.warnings,
                            model_uncertainty="medium",
                        ),
                    ),
                    best_opportunity=execution.market_id,
                    largest_risk="paper-only model uncertainty",
                    model_uncertainty="ensemble estimate",
                ),
            )
            saved_recommendations = read_prediction_recommendations(recommendations_path)
            saved_report = report_path.read_text(encoding="utf-8")

        self.assertEqual(execution.action, "BUY_YES")
        self.assertGreater(marked_row["mark_to_market_pnl"], 0.0)
        self.assertEqual(resolved_row["final_resolution"], "YES")
        self.assertGreater(resolved_row["realized_pnl"], 0.0)
        self.assertEqual(saved_recommendations[0]["action"], "BUY_YES")
        self.assertIn("paper-only research", report_markdown)
        self.assertEqual(saved_report, report_markdown)


if __name__ == "__main__":
    unittest.main()
