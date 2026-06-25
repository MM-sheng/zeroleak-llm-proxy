# Repository Notes

## GitHub

This project is currently uploaded here:

```text
https://github.com/MM-sheng/btc-pm-strategy
```

Use this remote and branch:

```text
origin: https://github.com/MM-sheng/btc-pm-strategy.git
branch: main
```

This project was originally staged as the `btc-pm-strategy` branch in
`MM-sheng/zeroleak-llm-proxy`. That was a temporary holding location. The
dedicated repository above is now the canonical home for BTC/Polymarket research.

## Project State

- Current project phase: Phase 9 complete.
- Remaining roadmap phase: Phase 10 live trading safety layer.
- Phase 10 status: locked.
- Current `NEXT` task: none, intentionally, because the only remaining phase is locked.
- Trading mode: paper-only.

## Useful Commands

```bash
python -m compileall src tests
python -m unittest discover -s tests -p 'test_*.py'
python -m src.main updown-backtest --data-source price_history --policy first_seen
```

## Local-Only Data

These paths are intentionally ignored by Git:

- `.env`
- `.pycache/`
- `data/raw/`
- `data/processed/`
- `data/paper_trading/`
- `data/updown_cache/`
- generated daily report output

The tracked research report is:

```text
reports/updown_price_history_backtest_report.md
```
