# AGENTS.md

Permanent operating rules for all future Codex sessions on this project.

## Project Goal

Build a professional BTC Polymarket probability and paper trading research system. The system scans BTC-related Polymarket markets, parses market questions, estimates model probabilities, compares them with market prices, computes edge, EV, risk, paper positions, backtests strategies, and produces Markdown reports.

This is a research system, not a gambling bot. The default mode is paper trading only.

## Hard Prohibitions

- Do not implement live trading unless a future task explicitly unlocks Phase 10 and `LIVE_TRADING=true`.
- Do not place real orders.
- Do not connect a wallet.
- Do not process or store wallet private keys.
- Do not hard-code API keys, wallet keys, secrets, or credentials.
- Do not create a real `.env` file.
- Do not use future data in backtests.
- Do not introduce look-ahead bias.
- Do not treat Polymarket market price as true probability.
- Do not output claims such as guaranteed profit, risk-free, sure win, or similar.
- Do not delete existing features unless a task explicitly requires it.
- Do not perform broad refactors outside the active task.

## Safety Rules

- All trading modules must default to paper-only behavior.
- `clob_client.py` must remain a safe stub until Phase 10 is explicitly unlocked.
- Every strategy recommendation must include risks, uncertainty, and reasons not to trade.
- All probabilities must be floats in `[0, 1]`.
- All times must be UTC.
- All USD values must state USD units.
- If design requirements conflict, record the conflict in `DECISIONS.md` before changing direction.

## Code Style

- Python code must be clear, typed where useful, and modular.
- Core functions must have docstrings.
- Prefer `dataclass` or `pydantic` models for structured data.
- API requests must include a timeout and explicit error handling.
- Do not use bare `except`.
- Use logging helpers rather than scattering `print`.
- Keep files focused and small.

## Testing Requirements

- Each module must be testable offline.
- External API behavior must be covered with mocks.
- Add or update tests with each behavior change.
- Run relevant tests before completing each task.
- If tests cannot run, document the exact reason in the final report and `CONTEXT.md`.

## File Modification Limits

- Only modify files needed for the active `NEXT` task.
- Do not rewrite governance files casually.
- Keep `CONTEXT.md` short and current.
- Keep `TASKS.md` authoritative, with exactly one `NEXT` task at all times.
- Update `DECISIONS.md` only for meaningful design decisions or conflicts.

## Per-Task Workflow

At the start of each task, read:

- `AGENTS.md`
- `PROJECT_SPEC.md`
- `TASKS.md`
- `DECISIONS.md`
- `CONTEXT.md`

Then output a Project State Summary of at most 10 lines:

- Current project goal
- Current phase
- Active task
- What this task will not do
- Expected files to modify
- Possible risks

During the task:

- Complete only the task marked `NEXT`.
- Keep changes scoped.
- Add tests when behavior is added.

At completion:

- Run relevant checks.
- Update `TASKS.md`.
- Update `CONTEXT.md`.
- Update `DECISIONS.md` if needed.
- Report modified files.
- Report test/check results.
- Report the next `NEXT` task.


## Codex + Claude Code Collaboration

This project is connected through the shared collaboration surface:

- Read `.collab/board.md`, `.collab/decisions.md`, and the latest handoff before editing.
- Use `CLAUDE.md` for the other agent's repo-level instructions.
- Work only on the current NEXT item unless the user explicitly changes priority.
- After work, update `.collab/handoffs/codex.md` with summary, verification, risks, and next action.
