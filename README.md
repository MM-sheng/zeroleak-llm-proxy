# BTC Polymarket Probability & Paper Trading Research System

Professional research scaffold for estimating BTC-related Polymarket event probabilities and running paper-only strategy analysis.

This project is not a gambling bot and is not investment advice. It does not place real trades.

## Current Supported Functionality

- Project governance files.
- Long-term task and context files for multi-session Codex handoff.
- Python package skeleton.
- Config placeholders.
- Paper-only safety defaults.
- BTC historical price loading through `BTCPriceLoader`, with `yfinance` as the default source for `BTC-USD`.
- Canonical BTC OHLCV schema:
  - `timestamp_utc`
  - `open`
  - `high`
  - `low`
  - `close`
  - `volume`
- BTC feature helpers:
  - one-period simple returns
  - one-period log returns
  - rolling annualized realized volatility
  - distance to target price in USD and percentage terms
- Offline Phase 1 tests using mocked data sources.

Polymarket scanning, probability models, strategy decisions, reports, paper trading, and CLI commands are planned but not implemented yet.

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

## Planned Usage

Future CLI commands:

```bash
python -m src.main scan
python -m src.main model --market-id MARKET_ID
python -m src.main report
python -m src.main paper
python -m src.main backtest
python -m src.main explain --market-id MARKET_ID
```

These commands are planned and not active yet.

## Not Yet Supported

- Polymarket Gamma API scanning.
- Polymarket CLOB trading.
- Wallet connection.
- Live order placement.
- Market question parsing.
- Probability modeling.
- Edge, EV, Kelly sizing, and trade decisions.
- Backtesting.
- Paper trading journal and reports.
- CLI commands.

## Safety

- Default mode is paper trading only.
- `LIVE_TRADING=false` is the required default.
- Do not commit `.env`.
- Do not store private keys in repository files.
- `src/polymarket/clob_client.py` is a locked safe stub until a future explicit live-trading safety phase.
- Phase 10 live trading is locked and must not be implemented without explicit future authorization and safety gates.

## Paper Trading

Paper trading means simulated decisions, simulated position sizes, and local journals. It does not place orders or connect to a wallet.

## Non-Investment Advice

Outputs from this project are research artifacts. They may be wrong, incomplete, stale, or poorly calibrated. They are not financial, legal, tax, or investment advice.
