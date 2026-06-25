"""Paper trading modules."""

from src.paper.journal import JOURNAL_FIELDS, PaperTradeJournal, append_journal_entry, read_journal
from src.paper.mark_to_market import mark_journal_row, mark_paper_execution
from src.paper.paper_executor import PaperExecution, PaperExecutionStatus, PaperSide, execute_paper_decision
from src.paper.recommendation_log import (
    RECOMMENDATION_FIELDS,
    PredictionRecommendation,
    RecommendationLog,
    read_prediction_recommendations,
    save_prediction_recommendation,
)
from src.paper.resolution import ManualResolution, resolve_journal_row, resolve_paper_execution

__all__ = [
    "JOURNAL_FIELDS",
    "PaperExecution",
    "PaperExecutionStatus",
    "PaperSide",
    "PaperTradeJournal",
    "PredictionRecommendation",
    "RECOMMENDATION_FIELDS",
    "RecommendationLog",
    "ManualResolution",
    "append_journal_entry",
    "execute_paper_decision",
    "mark_journal_row",
    "mark_paper_execution",
    "read_prediction_recommendations",
    "read_journal",
    "resolve_journal_row",
    "resolve_paper_execution",
    "save_prediction_recommendation",
]
