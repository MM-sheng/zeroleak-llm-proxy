# BTC Polymarket Probability & Paper Trading Research System

Paper-only research system for BTC-related Polymarket markets. It scans read-only
market data, parses BTC market questions, estimates probabilities, compares model
probability with market prices, sizes paper decisions, backtests strategies, and
generates Markdown reports.

This project is not a gambling bot and is not investment advice. It does not
place real trades.

## Repository Location

The uploaded Codex branch is:

```text
https://github.com/MM-sheng/zeroleak-llm-proxy/tree/btc-pm-strategy
```

Clone the project branch directly with:

```bash
git clone --branch btc-pm-strategy https://github.com/MM-sheng/zeroleak-llm-proxy.git btc_pm_strategy
```

The default branch of `MM-sheng/zeroleak-llm-proxy` belongs to another project.
Keep this BTC project on the `btc-pm-strategy` branch unless it is moved to a
dedicated repository.

## Current Status

- Phase 9 is complete.
- Phase 10 live trading is locked.
- There is intentionally no active `NEXT` task while the only remaining phase is locked.
- The project is paper-only and read-only for external trading systems.
- The latest tracked report is `reports/updown_price_history_backtest_report.md`.
- Local runtime cache under `data/updown_cache/` is ignored by Git and can be regenerated.

## Supported Functionality

- BTC OHLCV loading through `BTCPriceLoader`, with `yfinance` as the default
  source for `BTC-USD`.
- BTC feature helpers for returns, log returns, rolling realized volatility, and
  distance to target price.
- Read-only Polymarket Gamma market scanning and standardized BTC market schema.
- BTC market question parsing for target, direction, deadline, and touch vs.
  terminal event type.
- Historical volatility, Monte Carlo GBM, bootstrap fat-tail, ensemble, and
  calibration model helpers.
- YES/NO edge, expected value, Kelly sizing, risk checks, and paper-only trade
  decisions.
- Synthetic BTC backtests and read-only BTC Up/Down historical backtest helpers.
- Paper journal, mark-to-market, manual resolution, and local Markdown reports.
- CLI entry points for scan, model, report, paper, backtest, Up/Down backtest,
  and explain workflows.

## Install

```bash
cd btc_pm_strategy
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run Checks

```bash
python -m compileall src tests
python -m unittest discover -s tests -p 'test_*.py'
```

If `pytest` is installed in your environment, this project also keeps tests compatible with pytest-style collection:

```bash
python -m pytest
```

The default system Python in this workspace may not have `pytest` installed until dependencies are installed.

## CLI Usage

All commands are paper-only. Commands that read live public data may depend on
network and public API availability.

```bash
python -m src.main scan
python -m src.main model --market-id MARKET_ID
python -m src.main report
python -m src.main paper --market-id MARKET_ID --question "..." --action HOLD --model-probability 0.5
python -m src.main backtest
python -m src.main updown-backtest --data-source price_history --policy first_seen
python -m src.main explain --market-id MARKET_ID
```

## BTC Data Usage

Load BTC data from the default `BTC-USD` source:

```python
from src.data.btc_price_loader import BTCPriceLoader

prices = BTCPriceLoader().load_history(period="1y", interval="1d")
```

Add Phase 1 features:

```python
from src.data.btc_features import (
    add_distance_to_target_price,
    add_realized_volatility,
    add_returns,
)

features = add_returns(prices)
features = add_realized_volatility(features, window=30, periods_per_year=365)
features = add_distance_to_target_price(features, target_price=120000.0)
```

## Not Yet Supported

- Live order placement.
- Wallet connection.
- Real private-key handling.
- Production live trading.
- Any unattended execution that places orders.

## Safety

- Default mode is paper trading only.
- `LIVE_TRADING=false` is the required default.
- Do not commit `.env`.
- Do not store private keys in repository files.
- `src/polymarket/clob_client.py` is a locked safe stub until a future explicit live-trading safety phase.
- Phase 10 live trading is locked and must not be implemented without explicit future authorization and safety gates.

## Paper Trading

Paper trading means simulated decisions, simulated position sizes, and local journals. It does not place orders or connect to a wallet.

## Handoff Files

Future agents should read these files before editing:

- `AGENTS.md`
- `PROJECT_SPEC.md`
- `TASKS.md`
- `CONTEXT.md`
- `DECISIONS.md`
- `.collab/board.md`
- `.collab/decisions.md`
- latest file under `.collab/handoffs/`

## Non-Investment Advice

Outputs from this project are research artifacts. They may be wrong, incomplete, stale, or poorly calibrated. They are not financial, legal, tax, or investment advice.
