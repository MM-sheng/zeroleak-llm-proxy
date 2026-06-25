# DECISIONS.md

## 2026-06-07

- Date: 2026-06-07
- Decision: Bootstrap the repository as a governance-first, paper-only research system with Phase 10 locked.
- Reason: The project must be durable across multiple Codex sessions and must not depend on chat memory. Safety boundaries are central to the architecture.
- Alternatives considered: Build the full system immediately; implement scanner or model code first.
- Consequences: Phase 0 creates structure and long-term memory only. Business logic begins in Phase 1. Real trading remains unavailable.

- Date: 2026-06-24
- Decision: Do not mark Phase 10 as `NEXT` after completing Phase 9 because Phase 10 remains locked.
- Reason: `TASKS.md` requires exactly one `NEXT`, but the only remaining roadmap phase is explicitly `LOCKED` and requires future user unlock conditions.
- Alternatives considered: Mark Phase 10 as `NEXT`; add an invented housekeeping task.
- Consequences: Phase 9 can be marked complete, but `TASKS.md` temporarily has no `NEXT` until the user explicitly unlocks Phase 10 or adds a new non-live task.
