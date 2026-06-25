import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from src.reports import DailyReport, DailyReportMarket, render_daily_report, write_daily_report


class DailyReportTests(unittest.TestCase):
    def test_render_daily_report_contains_required_sections(self) -> None:
        report = DailyReport(
            generated_at_utc=datetime(2026, 1, 1, 8, tzinfo=timezone.utc),
            btc_current_state={"spot_price_usd": "$100,000 USD", "trend": "range-bound"},
            markets=(
                DailyReportMarket(
                    market_id="btc-100k",
                    question="Will Bitcoin hit $100,000 this week?",
                    yes_price=0.52,
                    no_price=0.48,
                    model_probability=0.61,
                    edge=0.09,
                    action="BUY_YES",
                    suggested_limit_price=0.52,
                    suggested_position_usd=10.0,
                    reasons_not_to_trade=("liquidity risk",),
                    model_uncertainty="medium",
                ),
            ),
            best_opportunity="btc-100k has the largest positive paper edge.",
            largest_risk="BTC gap risk around macro news.",
            model_uncertainty="Monte Carlo and bootstrap disagree moderately.",
        )

        markdown = render_daily_report(report)

        for heading in (
            "## BTC Current State",
            "## BTC Polymarket Markets Scanned Today",
            "## YES Price And NO Price Per Market",
            "## Model Probability",
            "## Edge",
            "## Action",
            "## Suggested Limit Price",
            "## Suggested Position",
            "## Reasons Not To Trade",
            "## Best Opportunity To Watch",
            "## Largest Risk",
            "## Model Uncertainty",
        ):
            self.assertIn(heading, markdown)
        self.assertIn("paper-only research", markdown)
        self.assertIn("btc-100k", markdown)
        self.assertIn("BUY_YES", markdown)
        self.assertIn("$10.00 USD", markdown)
        self.assertIn("liquidity risk", markdown)

    def test_write_daily_report_creates_markdown_file(self) -> None:
        report = DailyReport(
            generated_at_utc=datetime(2026, 1, 1, tzinfo=timezone.utc),
            btc_current_state={},
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "reports" / "daily_report.md"
            content = write_daily_report(output_path, report)
            saved = output_path.read_text(encoding="utf-8")

        self.assertEqual(saved, content)
        self.assertIn("No BTC markets scanned.", saved)

    def test_report_requires_timezone_aware_timestamp(self) -> None:
        report = DailyReport(generated_at_utc=datetime(2026, 1, 1), btc_current_state={})

        with self.assertRaises(ValueError):
            render_daily_report(report)


if __name__ == "__main__":
    unittest.main()
