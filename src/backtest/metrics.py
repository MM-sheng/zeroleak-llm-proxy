"""Backtest PnL and metrics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


BacktestSide = Literal["BUY_YES", "BUY_NO"]


@dataclass(frozen=True)
class BacktestMetrics:
    """Summary metrics for a sequence of closed paper trades."""

    total_return: float
    win_rate: float
    average_win: float
    average_loss: float
    max_drawdown: float
    profit_factor: float
    roi_per_trade: float
    largest_loss: float
    losing_streak: int
    number_of_trades: int
    exposure: float


def calculate_binary_trade_pnl(
    *,
    side: BacktestSide,
    entry_price: float,
    size_usd: float,
    resolved_yes: bool,
) -> float:
    """Calculate realized PnL for a closed binary YES/NO paper trade."""
    if side not in {"BUY_YES", "BUY_NO"}:
        raise ValueError("side must be BUY_YES or BUY_NO")
    price = float(entry_price)
    size = float(size_usd)
    if not 0.0 < price < 1.0:
        raise ValueError("entry_price must be between 0 and 1")
    if size < 0:
        raise ValueError("size_usd must be non-negative")

    winning_side = "BUY_YES" if resolved_yes else "BUY_NO"
    if side == winning_side:
        shares = size / price
        return shares - size
    return -size


def summarize_backtest_metrics(
    pnls: list[float] | tuple[float, ...],
    *,
    initial_bankroll_usd: float,
    exposures_usd: list[float] | tuple[float, ...] | None = None,
) -> BacktestMetrics:
    """Summarize closed-trade PnL metrics."""
    bankroll = float(initial_bankroll_usd)
    if bankroll <= 0:
        raise ValueError("initial_bankroll_usd must be positive")
    trades = [float(pnl) for pnl in pnls]
    if not trades:
        return BacktestMetrics(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0.0)

    wins = [pnl for pnl in trades if pnl > 0]
    losses = [pnl for pnl in trades if pnl < 0]
    total_pnl = sum(trades)
    equity = bankroll
    peak = bankroll
    max_drawdown = 0.0
    losing_streak = 0
    current_losing_streak = 0
    for pnl in trades:
        equity += pnl
        peak = max(peak, equity)
        max_drawdown = max(max_drawdown, (peak - equity) / peak if peak > 0 else 0.0)
        if pnl < 0:
            current_losing_streak += 1
            losing_streak = max(losing_streak, current_losing_streak)
        else:
            current_losing_streak = 0

    gross_profit = sum(wins)
    gross_loss = abs(sum(losses))
    exposures = [float(value) for value in exposures_usd] if exposures_usd is not None else []
    exposure = sum(exposures) / bankroll if exposures else 0.0
    return BacktestMetrics(
        total_return=total_pnl / bankroll,
        win_rate=len(wins) / len(trades),
        average_win=(gross_profit / len(wins)) if wins else 0.0,
        average_loss=(sum(losses) / len(losses)) if losses else 0.0,
        max_drawdown=max_drawdown,
        profit_factor=(gross_profit / gross_loss) if gross_loss > 0 else 0.0,
        roi_per_trade=(total_pnl / len(trades)) / bankroll,
        largest_loss=min(losses) if losses else 0.0,
        losing_streak=losing_streak,
        number_of_trades=len(trades),
        exposure=exposure,
    )
