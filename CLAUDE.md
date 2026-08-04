# CLAUDE.md

Thin context by design. This file points to the source of truth rather than
duplicating it — read the linked docs when a task touches those areas.

## What this repo is
A small USD→EUR exchange-rate workshop: a static dashboard (`usd_eur.html`) and
a pure, offline-testable rate core (`exchange_rates.py`).

## Where the real context lives
- **Specs** — `specs/*.md`. Every feature has a spec with numbered acceptance
  criteria (AC1, AC2, …). Build to the spec; if the spec is wrong, fix the spec
  first.
- **Decisions** — `docs/adr/*.md` (Architecture Decision Records). Read the
  relevant ADR before changing architecture; add a new ADR for a new decision.
- **Conventions** — `.claude/rules/conventions.md`.

## Workflow (how changes get made here)
Spec → build test-first (RED → GREEN) → review the diff against the spec with
the `reviewer` subagent → fix → commit → open a PR. A "done" change is one whose
acceptance criteria are proven by passing tests.

## Test commands
```
python3 -m unittest -v test_exchange_rates test_rate_summary
```
