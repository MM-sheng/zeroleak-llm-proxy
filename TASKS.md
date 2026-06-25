# TASKS.md

Allowed statuses: `TODO`, `NEXT`, `IN_PROGRESS`, `DONE`, `BLOCKED`, `LOCKED`.

Exactly one task may be marked `NEXT`.

## Phase 0: Project Governance

Goal: Establish the project skeleton and long-term memory system.

- 0.1 Create project directory structure. Status: DONE
- 0.2 Create `AGENTS.md`. Status: DONE
- 0.3 Create `PROJECT_SPEC.md`. Status: DONE
- 0.4 Create `TASKS.md`. Status: DONE
- 0.5 Create `DECISIONS.md`. Status: DONE
- 0.6 Create `CONTEXT.md`. Status: DONE
- 0.7 Create `README.md`. Status: DONE
- 0.8 Create `requirements.txt` and `.env.example`. Status: DONE
- 0.9 Create base `src` and `tests` directories. Status: DONE
- 0.10 Run basic checks. Status: DONE

Completion criteria:

- Project structure exists.
- Governance files exist.
- `TASKS.md` has exactly one `NEXT`.
- `CONTEXT.md` briefly records current state.
- No real trading logic exists.
- No real secrets exist.

## Phase 1: BTC Data System

Goal: Establish BTC historical price and feature system.

- 1.1 Implement `BTCPriceLoader`, prioritizing `yfinance` for `BTC-USD`. Status: DONE
- 1.2 Standardize DataFrame schema. Status: DONE
- 1.3 Implement returns calculation. Status: DONE
- 1.4 Implement realized volatility calculation. Status: DONE
- 1.5 Implement `distance_to_target_price` feature. Status: DONE
- 1.6 Write tests. Status: DONE
- 1.7 Update README usage. Status: DONE
- 1.8 Validate requested BTC data interval gaps. Status: DONE

Standard DataFrame schema:

- `timestamp_utc`
- `open`
- `high`
- `low`
- `close`
- `volume`

Requirements:

- Timestamps must be UTC.
- No duplicate timestamps.
- No clearly invalid prices.
- Missing data must be handled or raise.
- All functions must have docstrings.

## Phase 2: Polymarket Market Scanner

Goal: Scan BTC-related Polymarket markets in read-only mode.

- 2.1 Implement Gamma API client. Status: DONE
- 2.2 Implement `search_btc_markets()`. Status: DONE
- 2.3 Standardize market schema. Status: DONE
- 2.4 Filter closed, inactive, and low-liquidity markets. Status: DONE
- 2.5 Extract YES/NO price. Status: DONE
- 2.6 Write mock tests. Status: DONE
- 2.7 Update `CONTEXT.md`. Status: DONE

Standard market schema:

- `market_id`
- `question`
- `slug`
- `outcomes`
- `outcome_prices`
- `yes_price`
- `no_price`
- `volume`
- `liquidity`
- `end_date_utc`
- `active`
- `closed`
- `raw`

Prohibitions:

- Do not implement real order placement.
- Do not connect a wallet.
- Do not process private keys.
- Do not write CLOB trading logic. `clob_client.py` can only be a safe stub.

## Phase 3: Market Question Parser

Goal: Parse natural-language Polymarket BTC questions.

- 3.1 Define `ParsedMarket`. Status: DONE
- 3.2 Parse asset, target price, direction, event type, deadline, confidence, and warnings. Status: DONE
- 3.3 Distinguish touch probability from terminal probability. Status: DONE
- 3.4 Add tests for common question forms. Status: DONE
- 3.5 Update `CONTEXT.md`. Status: DONE

Output fields:

- `asset`
- `target_price`
- `direction`: `above`, `below`, or `unknown`
- `event_type`: `touch`, `terminal`, or `unknown`
- `deadline_utc`
- `confidence`
- `warnings`

## Phase 4: Probability Models

Goal: Estimate BTC touch or terminal probabilities before market deadlines.

- 4.1 Implement historical volatility model. Status: DONE
- 4.2 Implement Monte Carlo GBM model. Status: DONE
- 4.3 Implement bootstrap fat-tail model. Status: DONE
- 4.4 Implement ensemble model. Status: DONE
- 4.5 Implement model diagnostics output. Status: DONE
- 4.6 Write tests. Status: DONE

Monte Carlo input:

- `current_price`
- `target_price`
- `days_to_expiry`
- `annualized_volatility`
- `drift`
- `n_paths`
- `random_seed`
- `mode`: `touch` or `terminal`

Monte Carlo output:

- `probability`
- `terminal_probability`
- `touch_probability`
- `expected_max_price`
- `expected_min_price`
- `quantiles`
- `diagnostics`

## Phase 5: Edge, EV and Risk Engine

Goal: Convert model probability into paper-trading decisions.

- 5.1 Implement `edge_calculator`. Status: DONE
- 5.2 Implement expected value. Status: DONE
- 5.3 Implement Kelly sizing. Status: DONE
- 5.4 Implement `risk_manager`. Status: DONE
- 5.5 Implement `trade_decision`. Status: DONE
- 5.6 Write tests. Status: DONE

Formulas:

- `edge_yes = model_probability - yes_price`
- `edge_no = (1 - model_probability) - no_price`
- `EV_yes = model_probability * (1 - yes_price) - (1 - model_probability) * yes_price`
- `EV_no = (1 - model_probability) * (1 - no_price) - model_probability * no_price`
- `kelly_fraction = (p - price) / (1 - price)`

Risk constraints:

- Use quarter Kelly.
- Single trade risk <= 1% of bankroll.
- BTC similar-market aggregate risk <= 10% of bankroll.
- Stop after daily loss over 3%.
- Stop after weekly loss over 8%.
- Unclear rules mean no trade.
- Wide spread means no trade.
- Low liquidity means smaller size or no trade.

Output `TradeDecision`:

- `action`: `BUY_YES`, `BUY_NO`, or `HOLD`
- `model_probability`
- `market_price`
- `edge`
- `expected_value`
- `suggested_limit_price`
- `position_size_usd`
- `max_loss_usd`
- `confidence`
- `reasons`
- `warnings`

## Phase 6: Backtesting System

Goal: Validate whether the model can outperform market prices.

- 6.1 Generate synthetic BTC markets. Status: DONE
- 6.2 Generate weekly touch markets. Status: DONE
- 6.3 Estimate volatility using only prior data. Status: DONE
- 6.4 Enforce no future data usage. Status: DONE
- 6.5 Resolve touch markets using future high/low after simulated decision time. Status: DONE
- 6.6 Calculate PnL and strategy metrics. Status: DONE
- 6.7 Write tests. Status: DONE

Metrics:

- `total_return`
- `win_rate`
- `average_win`
- `average_loss`
- `max_drawdown`
- `profit_factor`
- `ROI_per_trade`
- `Brier score`
- `Log loss`
- `calibration by probability bucket`
- `largest_loss`
- `losing_streak`
- `number_of_trades`
- `exposure`

## Phase 7: Paper Trading and Reports

Goal: Scan real markets but only paper trade.

- 7.1 Implement `paper_executor`. Status: DONE
- 7.2 Implement trade journal. Status: DONE
- 7.3 Implement `daily_report.md`. Status: DONE
- 7.4 Save each model prediction and trade recommendation. Status: DONE
- 7.5 Support mark-to-market. Status: DONE
- 7.6 Support manual resolution entry. Status: DONE
- 7.7 Write tests. Status: DONE

Paper journal fields:

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

Daily report sections:

1. BTC current state.
2. BTC Polymarket markets scanned today.
3. YES price and NO price per market.
4. Model probability.
5. Edge.
6. Action.
7. Suggested limit price.
8. Suggested position.
9. Reasons not to trade.
10. Best opportunity to watch.
11. Largest risk.
12. Model uncertainty.

## Phase 8: CLI Integration

Goal: Provide one command-line entry point.

- 8.1 Implement `python -m src.main scan`. Status: DONE
- 8.2 Implement `python -m src.main model --market-id MARKET_ID`. Status: DONE
- 8.3 Implement `python -m src.main report`. Status: DONE
- 8.4 Implement `python -m src.main paper`. Status: DONE
- 8.5 Implement `python -m src.main backtest`. Status: DONE
- 8.6 Implement `python -m src.main explain --market-id MARKET_ID`. Status: DONE
- 8.7 Write CLI tests. Status: DONE

## Phase 9: Model Calibration

Goal: Prevent overconfident model output.

- 9.1 Record historical predictions. Status: DONE
- 9.2 Calculate Brier score. Status: DONE
- 9.3 Calculate Log loss. Status: DONE
- 9.4 Generate calibration curve. Status: DONE
- 9.5 Check realized hit rate by probability bucket. Status: DONE
- 9.6 Block strong buy signals if calibration is poor. Status: DONE
- 9.7 Build read-only BTC Up/Down data backtest helpers. Status: DONE
- 9.8 Add cached BTC Up/Down backtest runner. Status: DONE
- 9.9 Add BTC Up/Down backtest CLI wrapper. Status: DONE
- 9.10 Add skipped-window handling for slow Up/Down public API pulls. Status: DONE
- 9.11 Add grouped Up/Down backtest reporting by policy and market kind. Status: DONE
- 9.12 Add selectable Up/Down entry policy filters. Status: DONE
- 9.13 Add read-only CLOB price-history Up/Down backtests. Status: DONE

## Phase 10: Live Trading Safety Layer, LOCKED

Status: LOCKED

Do not implement Phase 10 now.

Future unlock conditions:

- Paper trading has at least 100 trades.
- Backtest results are positive.
- Max drawdown is acceptable.
- Model calibration is acceptable.
- `LIVE_TRADING=true`.
- User explicitly requests live trading.
- Human confirmation is required before each real order.
