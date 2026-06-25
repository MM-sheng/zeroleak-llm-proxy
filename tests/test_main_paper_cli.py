import io
import tempfile
import unittest
from pathlib import Path

from src.main import main
from src.paper import read_journal


class MainPaperCliTests(unittest.TestCase):
    def test_main_paper_appends_buy_to_journal(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            journal_path = Path(temp_dir) / "journal.jsonl"
            output = io.StringIO()

            exit_code = main(
                [
                    "paper",
                    "--journal",
                    str(journal_path),
                    "--market-id",
                    "btc-100k",
                    "--question",
                    "Will Bitcoin hit $100,000 this week?",
                    "--action",
                    "BUY_YES",
                    "--entry-price",
                    "0.50",
                    "--model-probability",
                    "0.65",
                    "--edge",
                    "0.15",
                    "--expected-value",
                    "0.15",
                    "--size-usd",
                    "10",
                ],
                out=output,
            )
            rows = read_journal(journal_path)

        self.assertEqual(exit_code, 0)
        self.assertIn("appended paper-only BUY_YES", output.getvalue())
        self.assertEqual(rows[0]["market_id"], "btc-100k")
        self.assertEqual(rows[0]["action"], "BUY_YES")
        self.assertEqual(rows[0]["size_usd"], 10.0)

    def test_main_paper_appends_hold_as_zero_position(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            journal_path = Path(temp_dir) / "journal.jsonl"

            exit_code = main(
                [
                    "paper",
                    "--journal",
                    str(journal_path),
                    "--market-id",
                    "btc-hold",
                    "--question",
                    "Will Bitcoin hold?",
                    "--action",
                    "HOLD",
                    "--model-probability",
                    "0.50",
                ],
                out=io.StringIO(),
            )
            rows = read_journal(journal_path)

        self.assertEqual(exit_code, 0)
        self.assertEqual(rows[0]["action"], "HOLD")
        self.assertEqual(rows[0]["side"], "NONE")
        self.assertEqual(rows[0]["size_usd"], 0.0)


if __name__ == "__main__":
    unittest.main()
