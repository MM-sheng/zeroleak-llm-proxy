# BTC Up/Down Price-History Backtest Report

Date: 2026-06-25

## 1. Scope

This report records the full read-only investigation and implementation flow for BTC Up/Down Polymarket backtests after the user asked to continue searching for data and run backtests with a new data source.

The work stayed inside the current project safety boundary:

- No live trading.
- No wallet connection.
- No real orders.
- No private keys or API keys.
- No `.env` creation.
- No Phase 10 implementation.

## 1.1 Executive Summary

The project tested a simple family of BTC Up/Down market-entry timing policies against historical Polymarket market data. The initial Data API trades-based backtest produced an apparently strong `last_before_end` result, but that result did not survive when the market history source was changed to CLOB `prices-history`.

Final working interpretation:

- The strategy is not currently profitable based on the more reliable price-history sample.
- `first_seen` and `first_start_window` were nearly flat but slightly negative over the 180-minute price-history sample.
- `last_before_end` looked strong in sparse trade data but became clearly negative in price-history data.
- The apparent old edge is best treated as a data-source artifact, not as a trading edge.
- The next engineering priority is not live trading. It is cache-only/offline backtest reliability and larger historical samples.

Best current result by reliability-adjusted judgment:

| Data source | Policy | Lookback | Entries | total_return | max_drawdown | Judgment |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| CLOB price-history | first_seen | 180m | 94 | -0.0106 | 0.0366 | Slightly negative, usable baseline |
| CLOB price-history | first_start_window | 180m | 94 | -0.0106 | 0.0366 | Same as first_seen in this sample |
| CLOB price-history | last_before_end | 180m | 94 | -0.2027 | 0.2133 | Rejected |
| Data API trades cache | last_before_end | cache sample | 72 | 1.6871 | 0.1943 | Rejected as likely artifact |

Bottom line: the current timing-only strategy should remain research-only and paper-only.

## 2. Starting Point

The project already had a paper-only BTC Polymarket research system with:

- read-only Gamma event discovery,
- BTC Coinbase candles for market resolution,
- Polymarket Data API trade-cache based Up/Down backtests,
- policy grouping by `first_seen`, `first_start_window`, and `last_before_end`,
- selectable policy filters in the CLI.

The prior Data API trades workflow produced useful early samples but had a practical issue: larger live lookbacks could stall while reading Polymarket Data API trade responses.

## 3. External API Material Reviewed

The user provided a Solana API note covering Birdeye, GeckoTerminal, and Dune. It was useful as a general data-pipeline reference, especially for:

- chunked historical OHLCV pulls,
- rate-limit handling,
- avoiding polluted empty caches,
- treating API keys as secrets.

However, it was not directly suitable for the BTC Polymarket project because this project needs BTC Polymarket market history rather than Solana token OHLCV. The useful action from that note was to keep looking for a more reliable read-only market-data source and to avoid hard-coded keys.

Important security observation: the pasted note contained apparent real API keys. Those were not copied into project files or code and should be treated as exposed credentials outside this repository.

## 4. Data Source Decision

The new data source selected was Polymarket CLOB `prices-history`.

Why:

- It is read-only market data.
- It does not require wallet signing.
- It does not require API keys for public reads.
- It returns market price points directly for outcome token ids.
- It avoids the slow Data API trade-response path observed in larger pulls.

Gamma event cache already contained `clobTokenIds` and `outcomes`, so each Up/Down event could map:

- `Up` -> one CLOB token id,
- `Down` -> one CLOB token id.

The public CLOB response shape verified during probing was:

```json
{
  "history": [
    {"t": 1782358204, "p": 0.455}
  ]
}
```

## 5. Implementation Summary

Implemented a second data path for `updown-backtest`:

```bash
python3 -m src.main updown-backtest \
  --lookback-minutes 180 \
  --cache-dir data/updown_cache \
  --data-source price_history \
  --policy first_seen
```

Code changes:

- Added `UpDownPricePoint`.
- Extracted Gamma `outcomes` and `clobTokenIds` into `UpDownWindow.outcome_token_ids`.
- Added CLOB `prices-history` fetcher.
- Added parser for `history: [{t, p}]`.
- Added cached storage under `data/updown_cache/prices/`.
- Added `simulate_updown_price_entries()` using the same entry policies as the trades path.
- Added `--data-source` CLI flag with choices:
  - `trades`
  - `price_history`

The old trades path remains the default to avoid breaking existing behavior.

## 5.1 Strategy Definition

The tested strategy is not a full predictive BTC model yet. It is a market-entry timing experiment over BTC Up/Down binary markets.

Each market has two outcomes:

- `Up`
- `Down`

Each simulated entry buys one outcome token at a historical observed market price and resolves it against BTC movement over the market window. PnL is calculated as a binary YES-style paper trade:

- If the selected outcome wins, the position pays out according to entry price and size.
- If the selected outcome loses, the entry loses its stake.

Fixed assumptions used in the reported runs:

- Paper size per entry: 10 USD.
- Initial paper bankroll for metrics: 1000 USD.
- Resolution proxy: Coinbase BTC/USD one-minute candles.
- Market data source for final results: Polymarket CLOB `prices-history`.

Entry timing policies:

| Policy | Meaning | Main risk |
| --- | --- | --- |
| `first_seen` | Enter at the first available observed market price for each outcome. | Can be too early and uninformed. |
| `first_start_window` | Enter during the early part of the market window. | Often identical to `first_seen` when first prices arrive inside the start window. |
| `last_before_end` | Enter at the last observed price before market end. | High risk of near-resolution leakage or untradeable late pricing. |

The current strategy does not yet include:

- model probability,
- expected value filtering,
- spread filtering,
- slippage,
- order-book depth,
- fees,
- live fill assumptions,
- latency assumptions.

Therefore the current strategy layer is only a diagnostic timing policy, not a deployable trading strategy.

## 6. Backtest Runs

### 6.1 Prior Data API Trades Observations

The larger 180-minute trades runs were interrupted after getting stuck in Polymarket Data API trade response streaming. This indicated that the old trades source was not reliable enough for larger interactive lookbacks.

An offline cache analysis before switching fully to price-history showed:

| Metric | Value |
| --- | ---: |
| Cached windows | 67 |
| Cached entries | 154 |
| Missing trade cache | 31 |
| Overall total_return | 1.5850 |
| Overall win_rate | 0.5000 |
| Overall max_drawdown | 0.2699 |

Grouped by policy from trades cache:

| Policy | Trades | total_return | win_rate | max_drawdown |
| --- | ---: | ---: | ---: | ---: |
| first_seen | 72 | -0.1075 | 0.5000 | 0.1388 |
| first_start_window | 10 | 0.0054 | 0.5000 | 0.0198 |
| last_before_end | 72 | 1.6871 | 0.5000 | 0.1943 |

Interpretation: the strong `last_before_end` result looked suspicious because it was near settlement and came from sparse trade observations. It was treated as a possible data artifact, not as a tradable edge.

### 6.2 New CLOB Price-History Results

#### 60-minute price-history sample

Command:

```bash
python3 -m src.main updown-backtest \
  --lookback-minutes 60 \
  --cache-dir data/updown_cache \
  --data-source price_history \
  --policy first_seen
```

Result:

| Metric | Value |
| --- | ---: |
| windows | 15 |
| skipped_windows | 0 |
| entries | 30 |
| number_of_trades | 30 |
| total_return | -0.0034 |
| win_rate | 0.5000 |
| max_drawdown | 0.0269 |
| exposure | 0.3000 |

Grouped by kind:

| Kind | Trades | total_return | win_rate | max_drawdown |
| --- | ---: | ---: | ---: | ---: |
| 15m | 6 | -0.0021 | 0.5000 | 0.0198 |
| 5m | 24 | -0.0013 | 0.5000 | 0.0256 |

#### 180-minute price-history, `first_seen`

Command:

```bash
python3 -m src.main updown-backtest \
  --lookback-minutes 180 \
  --cache-dir data/updown_cache \
  --data-source price_history \
  --policy first_seen
```

Result:

| Metric | Value |
| --- | ---: |
| windows | 47 |
| skipped_windows | 0 |
| entries | 94 |
| number_of_trades | 94 |
| total_return | -0.0106 |
| win_rate | 0.5000 |
| max_drawdown | 0.0366 |
| exposure | 0.9400 |

Grouped by kind:

| Kind | Trades | total_return | win_rate | max_drawdown |
| --- | ---: | ---: | ---: | ---: |
| 15m | 22 | -0.0047 | 0.5000 | 0.0221 |
| 5m | 72 | -0.0059 | 0.5000 | 0.0328 |

#### 180-minute price-history, all policies

Command:

```bash
python3 -m src.main updown-backtest \
  --lookback-minutes 180 \
  --cache-dir data/updown_cache \
  --data-source price_history
```

Result:

| Metric | Value |
| --- | ---: |
| windows | 47 |
| skipped_windows | 0 |
| entries | 282 |
| number_of_trades | 282 |
| total_return | -0.2240 |
| win_rate | 0.5000 |
| max_drawdown | 0.2515 |
| exposure | 2.8200 |

Grouped by policy:

| Policy | Trades | total_return | win_rate | max_drawdown |
| --- | ---: | ---: | ---: | ---: |
| first_seen | 94 | -0.0106 | 0.5000 | 0.0366 |
| first_start_window | 94 | -0.0106 | 0.5000 | 0.0366 |
| last_before_end | 94 | -0.2027 | 0.5000 | 0.2133 |

Grouped by kind:

| Kind | Trades | total_return | win_rate | max_drawdown |
| --- | ---: | ---: | ---: | ---: |
| 15m | 66 | -0.1157 | 0.5000 | 0.1158 |
| 5m | 216 | -0.1083 | 0.5000 | 0.1448 |

#### 180-minute price-history, `last_before_end`

Command:

```bash
python3 -m src.main updown-backtest \
  --lookback-minutes 180 \
  --cache-dir data/updown_cache \
  --data-source price_history \
  --policy last_before_end
```

Result:

| Metric | Value |
| --- | ---: |
| windows | 47 |
| skipped_windows | 0 |
| entries | 94 |
| number_of_trades | 94 |
| total_return | -0.2027 |
| win_rate | 0.5000 |
| max_drawdown | 0.2133 |
| exposure | 0.9400 |

Grouped by kind:

| Kind | Trades | total_return | win_rate | max_drawdown |
| --- | ---: | ---: | ---: | ---: |
| 15m | 22 | -0.1062 | 0.5000 | 0.1063 |
| 5m | 72 | -0.0965 | 0.5000 | 0.1148 |

### 6.3 Consolidated Result Matrix

| Run | Source | Lookback | Policy | Windows | Entries | Skipped | total_return | win_rate | max_drawdown | Exposure |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A | Data API trades cache | cache sample | all | 67 | 154 | n/a | 1.5850 | 0.5000 | 0.2699 | n/a |
| B | Data API trades cache | cache sample | first_seen | n/a | 72 | n/a | -0.1075 | 0.5000 | 0.1388 | n/a |
| C | Data API trades cache | cache sample | first_start_window | n/a | 10 | n/a | 0.0054 | 0.5000 | 0.0198 | n/a |
| D | Data API trades cache | cache sample | last_before_end | n/a | 72 | n/a | 1.6871 | 0.5000 | 0.1943 | n/a |
| E | CLOB price-history | 60m | first_seen | 15 | 30 | 0 | -0.0034 | 0.5000 | 0.0269 | 0.3000 |
| F | CLOB price-history | 180m | first_seen | 47 | 94 | 0 | -0.0106 | 0.5000 | 0.0366 | 0.9400 |
| G | CLOB price-history | 180m | all | 47 | 282 | 0 | -0.2240 | 0.5000 | 0.2515 | 2.8200 |
| H | CLOB price-history | 180m | last_before_end | 47 | 94 | 0 | -0.2027 | 0.5000 | 0.2133 | 0.9400 |

## 7. Key Findings

1. CLOB price-history is materially more stable than Data API trades for this workflow.
   - The 180-minute price-history run completed with 47 windows and 0 skipped windows.
   - The earlier 180-minute trades run stalled on public trade response streaming.

2. The old `last_before_end` outperformance was likely a data artifact.
   - Trades-cache analysis showed `last_before_end` total_return of 1.6871.
   - Price-history analysis showed `last_before_end` total_return of -0.2027.
   - The latter is more believable because it samples the market price history directly instead of only observed trades.

3. `first_seen` and `first_start_window` were close to flat but slightly negative in the 180-minute price-history sample.
   - Both had total_return -0.0106 over 94 entries.
   - This is not evidence of a positive edge.

4. The current policy set is descriptive, not predictive.
   - It tests timing rules against historical prices.
   - It does not estimate fair probability.
   - It should not be used as a live trading signal.

## 7.1 Strategy Problems Encountered

### Problem 1: Data API trades are sparse and biased

The trades endpoint only shows actual trades. It does not guarantee a continuous view of the market price. That creates several risks:

- quiet markets may have no trades,
- the last trade may be stale,
- a trade near market end may reflect information not available earlier,
- observed trades may overrepresent certain market conditions,
- missing trade cache can make samples inconsistent.

Effect on results:

- The Data API trades cache made `last_before_end` look extremely profitable.
- The same policy became clearly negative with CLOB price-history.

Decision:

- Treat trades-based timing results as exploratory only.
- Prefer CLOB price-history for timing-policy backtests.

### Problem 2: `last_before_end` is structurally suspicious

The `last_before_end` policy samples the last observed price before resolution. Even when this is not literal future leakage, it is close enough to settlement to be dangerous.

Issues:

- It may capture market participants already reacting to near-final BTC movement.
- It may not be realistically fillable.
- It can collapse into betting on almost-known outcomes.
- It can overstate backtest performance if sampled from sparse data.

Effect on results:

- Trades cache: `last_before_end` total_return 1.6871.
- Price-history: `last_before_end` total_return -0.2027.

Decision:

- Reject `last_before_end` as a candidate strategy until a stricter no-late-entry rule and fillability model exist.

### Problem 3: Timing rules do not create an edge by themselves

The current policies only choose when to sample a market price. They do not decide whether the price is mispriced.

Missing components:

- model probability,
- market implied probability comparison,
- expected value threshold,
- calibration guard,
- spread/liquidity guard,
- risk sizing.

Effect on results:

- `first_seen` and `first_start_window` were close to flat but negative in price-history data.
- Win rate stayed at 0.5000 because both Up and Down sides are sampled symmetrically.

Decision:

- The timing-policy backtest is useful for data validation.
- It is not enough to define a final strategy.

### Problem 4: External API dependency blocks repeatable research

After the report was drafted, a repeat attempt to run the same 180-minute price-history commands stalled in CLOB API connection/SSL handshake. The processes were manually interrupted. This did not invalidate the earlier successful results, but it highlighted a workflow weakness.

Observed blocker:

- The command entered `fetch_clob_price_history()`.
- It stalled during public CLOB HTTPS connection setup.
- It required manual interruption.

Decision:

- Add `cache-only` or `offline` mode before expanding to larger lookbacks.
- Do not rely on public API live availability for every analysis run.

### Problem 5: Resolution is approximate

The market is resolved using Coinbase BTC/USD one-minute candles as a proxy. That is practical, but it may not exactly match Polymarket's actual resolution source for every window.

Risks:

- candle timestamp alignment may differ,
- market resolution source may use a different index,
- boundary behavior around equal open/close may matter,
- one-minute granularity can hide intra-minute movement.

Decision:

- Keep current proxy for research,
- label results as approximate,
- avoid live-trading interpretation.

## 7.2 Strategy Status

Current status by policy:

| Policy | Status | Reason |
| --- | --- | --- |
| `first_seen` | Keep as baseline | Clean, early, low drawdown, but slightly negative. |
| `first_start_window` | Keep as baseline variant | Same result as first_seen in current price-history sample. |
| `last_before_end` | Reject for now | Negative on price-history and structurally vulnerable to late-information bias. |
| all policies mixed | Do not use as strategy | Mixes incompatible timing assumptions and worsens drawdown. |

Current strategy verdict:

- No production or live strategy exists.
- No positive edge has been validated.
- The new data source is useful.
- The best next strategy work is probability/EV filtering on top of `first_seen` or early-window entries.

## 8. Verification

Commands run successfully:

```bash
python3 -m compileall src tests
python3 -m unittest tests.test_updown_market_backtest tests.test_main_updown_backtest_cli
python3 -m unittest discover -s tests -p 'test_*.py'
```

Observed test result:

- Focused tests: 10 passed.
- Full unittest discovery: 194 passed.

Safety checks:

```bash
python3 - <<'PY'
from pathlib import Path
root = Path.cwd()
text = (root / 'TASKS.md').read_text(encoding='utf-8')
assert text.count('Status: NEXT') == 0
assert 'Phase 10: Live Trading Safety Layer, LOCKED' in text
assert not (root / '.env').exists()
print('state checks passed')
PY
```

Secret/live-action scan was also run. The only hit was the expected governance test assertion checking `.env.example` placeholder text.

Additional repeat-run note:

- A later attempt to re-run 180-minute price-history commands stalled on public CLOB API connection setup.
- The processes were interrupted.
- This is now recorded as evidence that cache-only/offline mode is required for reliable research operations.

## 9. Files Changed During Implementation

- `src/backtest/updown_market_backtest.py`
- `src/main.py`
- `tests/test_updown_market_backtest.py`
- `TASKS.md`
- `CONTEXT.md`
- `.collab/handoffs/codex.md`

Generated cache:

- `data/updown_cache/prices/`
- 94 files, approximately 376 KB after the 180-minute price-history runs.

## 10. Current Limitations

- The first price-history fetch still depends on public Polymarket CLOB API availability.
- Larger lookbacks may be slow on first fetch, even though cached reruns are fast.
- The BTC resolution currently uses Coinbase candles as an approximation.
- The sample size is still small.
- The backtest tests entry timing rules, not a full probability model.
- Phase 10 remains locked.

## 11. Recommended Next Steps

1. Add a `cache-only` or `offline` mode for `updown-backtest`.
   - This will let analysis run only over already cached windows.
   - It prevents public API delays from blocking research.

2. Add CSV/Markdown export for grouped price-history backtest results.
   - This will make comparisons easier across lookbacks and policies.

3. Expand price-history lookbacks after cache-only mode exists.
   - Suggested windows: 6h, 12h, 24h, then multi-day if stable.

4. Compare price-history sampled entries against model probabilities.
   - Current runs only test entry timing.
   - A stronger research step is to add BTC probability estimates before each window and evaluate calibration/EV.

5. Keep all work paper-only.
   - No live trading path should be added unless Phase 10 is explicitly unlocked later.

## 12. Final Research Conclusion

The project successfully moved from a fragile trades-based market-history workflow to a more reliable CLOB price-history workflow. The new data source produced cleaner and less flattering results, which is a good outcome for research quality.

The important conclusion is not that the strategy works. The important conclusion is that the earlier apparent edge did not survive better data.

Current best interpretation:

- `last_before_end` should be rejected.
- `first_seen` and `first_start_window` are acceptable baselines but not profitable yet.
- Larger cache-backed samples are required.
- A real research strategy must combine early market prices with model probabilities, EV, calibration, spread/liquidity checks, and paper-only risk controls.

Until those pieces are added and validated, this remains a data and backtest infrastructure milestone, not a deployable strategy.
