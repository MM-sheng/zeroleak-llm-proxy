# Trading Research Asset Classification

Generated: 2026-06-26 Asia/Shanghai.

This public summary classifies the trading research assets without exposing
local filesystem paths, account-specific blockers, credentials, private notes,
or detailed strategy inventories. It is not trading advice and it is not a live
signal list.

## Summary

The research assets are separated into seven categories:

| Class | Name | Use | Public Handling |
|---|---|---|---|
| A | Core strategy research | Offline research and backtesting | Keep high-level only |
| B | Polymarket research | Paper-only BTC/PM research | Keep paper-only safety notes |
| C | Data/API tooling | Reusable public-data clients | Document APIs, not keys |
| D | Risk and feature research | Filters, sizing, and risk gates | Keep as safety layer |
| E | Backtesting frameworks | Reusable no-lookahead backtest code | Keep framework-level docs |
| F | Macro/cross-asset observation | Event watchlists and market context | Keep non-account-specific |
| G | Live-trading boundaries | Human-only gates and credentials | Do not publish details |

## A. Core Strategy Research

The most mature non-Polymarket line is a Binance-style multi-strategy research
track with cached market data, backtest tables, parameter scans, and status
reports.

Public-safe notes:

- Treat all results as research only.
- Do not promote cache-only outputs as live-trading signals.
- Keep exchange-account, region, position, and permission details out of public
  documents.

## B. Polymarket / BTC Research

The BTC/Polymarket project is now maintained in this dedicated repository:

```text
https://github.com/MM-sheng/btc-pm-strategy
```

Public-safe notes:

- Phase 9 research is complete.
- Phase 10 live trading remains locked.
- No wallet, private key, signed order, or real trade path belongs in the public
  repository.
- Existing reports should stay paper-only and should not include local machine
  paths or credential-status details.

## C. Data And API Tooling

The reusable data/API layer includes public market-data APIs, exchange market
data, on-chain analytics APIs, and price/candle sources.

Public-safe notes:

- API names and public documentation links are fine.
- API keys, account IDs, private endpoints, local proxy details, and credential
  setup notes should remain private.
- Example configs must use empty placeholders only.

## D. Risk And Feature Research

Risk research includes funding, open interest, liquidation, volume, volatility,
position sizing, kill switches, and paper execution helpers.

Public-safe notes:

- Publish risk concepts and code only when they contain no account or credential
  assumptions.
- Keep real thresholds, account constraints, and live-readiness notes private
  unless intentionally sanitized.

## E. Reusable Backtesting Frameworks

Reusable backtest components include strategy interfaces, fill models, regime
detection, position sizing, risk management, and sample data.

Public-safe notes:

- Keep no-lookahead and next-bar fill assumptions explicit.
- Do not include proprietary data dumps or account-specific execution settings.

## F. Macro / Cross-Asset Observation

Macro and cross-asset work should remain observational unless a future dedicated
project defines a tested workflow.

Public-safe notes:

- Public watchlists should avoid account, subscription, and broker permission
  details.
- Broker setup notes and subscription status should stay private.

## G. Live-Trading Boundaries

Live-trading readiness is a private operational topic. Public repositories should
only state the boundary, not the account-specific details.

Never publish:

- `.env` files or filled credential templates.
- API keys, private keys, seed phrases, wallet signing details, or exchange
  secrets.
- Account status, balance, positions, broker permissions, or region-specific
  access blockers.
- Local machine paths that reveal the private workspace layout.
- Detailed live-entry or live-execution gates tied to a personal account.

## Recommended Public Repository Split

| Repository | Public Contents | Keep Private |
|---|---|---|
| `btc-pm-strategy` | BTC/PM paper research, tests, sanitized reports | Live credentials, account notes, local paths |
| `polymarket-reward-scanner` | Reward-market scanner logic and paper simulation | Wallets, private keys, execution notes |
| `crypto-strategy-bot` | Backtest framework and sanitized results | Exchange credentials and account status |
| `crypto-risk-research` | Risk feature library and tests | Account-specific limits |
| `dune-birdeye-kit` | API client and examples | API keys and query secrets |
| `mean-reversion-strategy` | Generic event-driven backtest framework | Proprietary data and live settings |

## Public Safety Checklist

Before making any trading repository public:

1. Run a secret scan.
2. Search for local absolute paths.
3. Search for account, region, balance, position, wallet, and credential terms.
4. Keep only sanitized reports.
5. Confirm `.env` is ignored and only `.env.example` is committed.
6. Confirm generated caches and raw data dumps are ignored.

