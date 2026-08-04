# ADR 0001 — Pure, dependency-injected rate core

Status: Accepted

## Context
The USD→EUR dashboard needs rate logic (date ranges, response parsing, deltas,
summaries). If that logic reaches out to the network directly, it becomes slow
and flaky to test, and it can't run offline. The sandboxes this repo is
developed in also block outbound HTTP, so networked logic can't be exercised at
all during development.

## Decision
Keep `exchange_rates.py` **pure and free of I/O**:
- No network imports at module import time.
- All fetching is injected as a callable (`fetch_day(date) -> point | None`),
  supplied by the caller (the browser/dashboard or a script).
- Functions take plain data and return plain data, so they are trivially unit
  tested without mocks or a network.

## Consequences
- Every behaviour is covered by fast, offline `unittest` cases.
- Providers (Currency API, Frankfurter) live at the edges, not in the core.
- New analytics (e.g. a 7-day summary) are added as pure functions over the
  already-fetched series, following this same rule.
