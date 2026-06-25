# Codex + Claude Code Collaboration

This repo is connected to Codex through the shared collaboration files:

- `.collab/board.md` for current task state
- `.collab/decisions.md` for durable decisions
- `.collab/handoffs/codex.md` for Codex handoffs
- `.collab/handoffs/claude.md` for Claude Code handoffs
- `AGENTS.md` for shared agent rules

## Required Start

Before editing files:

1. Read `AGENTS.md`.
2. Read `.collab/board.md`.
3. Read `.collab/decisions.md`.
4. Read the latest relevant handoff in `.collab/handoffs/`.
5. Run `git status`.

## Collaboration Rule

Work only on the current `NEXT` item unless the user explicitly changes priority. After work, update `.collab/handoffs/claude.md`.
