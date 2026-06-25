# Repository Notes

## GitHub

This project is currently uploaded here:

```text
https://github.com/MM-sheng/zeroleak-llm-proxy/tree/btc-pm-strategy
```

Use this remote and branch:

```text
origin: https://github.com/MM-sheng/zeroleak-llm-proxy.git
branch: btc-pm-strategy
```

The repository default branch contains a different project. Do not merge this
branch into `main` unless the repository is intentionally repurposed.

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
