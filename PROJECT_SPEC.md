# PROJECT_SPEC.md

## Project Goal

BTC Polymarket Probability & Paper Trading Research System estimates whether BTC-related Polymarket prices offer research-worthy edge. It scans BTC markets, parses questions, loads BTC price data, estimates true event probabilities, compares them with market prices, computes EV and risk, records paper trades, backtests model behavior, and produces Markdown reports.

The system is paper-only by default and must never place real trades in the current locked roadmap.

## System Architecture

- `src/data/`: BTC price loading, standardized OHLCV schema, features, macro data stubs.
- `src/polymarket/`: read-only Polymarket market discovery and safe CLOB stub.
- `src/parser/`: natural-language market question parsing.
- `src/models/`: volatility, Monte Carlo, bootstrap, ensemble, and calibration models.
- `src/strategy/`: edge, EV, Kelly sizing, risk controls, and trade decisions.
- `src/backtest/`: synthetic market generation, no-look-ahead simulation, and metrics.
- `src/paper/`: paper executor and journal.
- `src/reports/`: daily Markdown report generation.
- `src/utils/`: logging, UTC time helpers, probability and math helpers.
- `config/`: non-secret settings and market filters.
- `data/`: local raw, processed, and paper-trading artifacts.
- `reports/`: generated reports.
- `tests/`: offline unit tests and mock integration tests.

## Data Sources

- BTC historical and current data: initially `yfinance` for `BTC-USD`.
- Polymarket BTC markets: Gamma API, read-only.
- Polymarket CLOB: locked safe stub until a future explicit Phase 10 unlock.
- Macro data: placeholder for future read-only sources.

No API keys or secrets are committed. Optional credentials belong only in a local `.env` that is not created by this project bootstrap.

## Model Design

All model probabilities are floats in `[0, 1]`.

Initial probability models:

- Historical realized volatility model.
- Monte Carlo GBM model with deterministic `random_seed` support.
- Bootstrap fat-tail model using historical return samples.
- Ensemble model combining model outputs and diagnostics.
- Calibration layer using historical predictions and realized outcomes.

Models must distinguish:

- `touch`: probability that BTC reaches or crosses a target before deadline.
- `terminal`: probability that BTC closes above or below a target at deadline.

## Strategy Logic

For each parsed market:

1. Estimate model probability.
2. Read market YES and NO prices.
3. Compute YES and NO edge.
4. Compute expected value.
5. Apply risk controls and liquidity filters.
6. Output `BUY_YES`, `BUY_NO`, or `HOLD`.

The market price is an input, not a true probability oracle.

## Risk Logic

- Use quarter Kelly only after base Kelly is computed.
- Single-market max risk: 1% of bankroll.
- BTC correlated market aggregate max risk: 10% of bankroll.
- Stop after daily loss over 3%.
- Stop after weekly loss over 8%.
- Do not trade when rules are unclear.
- Do not trade when spread is too wide or liquidity is too low.
- Every decision must include reasons and warnings.

## Backtesting Logic

Phase 6 starts with synthetic BTC markets, not historical Polymarket data.

Backtests must:

- Use only data available before the simulated decision time.
- Avoid look-ahead bias.
- Generate weekly touch markets such as +5%, +10%, and -5% targets.
- Estimate volatility using past data only.
- Resolve touch events using future high/low only after trade time.
- Report PnL, drawdown, win rate, calibration, Brier score, log loss, exposure, and streak metrics.

## Paper Trading Logic

Paper trading stores simulated orders and marks them to market. It never places real orders.

Journal fields:

- `timestamp_utc`
- `market_id`
- `question`
- `action`
- `side`
- `entry_price`
- `model_probability`
- `edge`
- `size_usd`
- `rationale`
- `current_price`
- `mark_to_market_pnl`
- `final_resolution`
- `realized_pnl`
- `lesson`

## Report Output

Daily Markdown reports must include:

- BTC current state.
- BTC Polymarket markets scanned.
- YES and NO prices.
- Model probabilities.
- Edge and action.
- Suggested limit price and paper position size.
- Reasons not to trade.
- Most notable opportunity.
- Largest risk.
- Model uncertainty.

## CLI Commands

Planned commands:

```bash
python -m src.main scan
python -m src.main model --market-id MARKET_ID
python -m src.main report
python -m src.main paper
python -m src.main backtest
python -m src.main explain --market-id MARKET_ID
```

## Long-Term Roadmap

- Phase 0: Project Governance
- Phase 1: BTC Data System
- Phase 2: Polymarket Market Scanner
- Phase 3: Market Question Parser
- Phase 4: Probability Models
- Phase 5: Edge, EV and Risk Engine
- Phase 6: Backtesting System
- Phase 7: Paper Trading and Reports
- Phase 8: CLI Integration
- Phase 9: Model Calibration
- Phase 10: Live Trading Safety Layer, LOCKED

Phase 10 is locked and must not be implemented unless all safety conditions are satisfied and the user explicitly requests it.

