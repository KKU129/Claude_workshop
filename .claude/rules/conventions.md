# Conventions

Keep this short. These are the rules a reviewer checks against.

## Core logic
- The rate core (`exchange_rates.py`) is **pure and I/O-free on import**.
  Networking is injected via callables (e.g. `fetch_day`); never import
  `urllib`/`requests`/`httpx` at module top level. See
  `docs/adr/0001-pure-rate-core.md`.
- Public functions take plain data in and return plain data out (dicts, lists,
  tuples). No global mutable state.

## Numbers
- Round derived rate values to **4 decimals** to avoid floating-point noise in
  output (e.g. `1.3`, not `1.3000000000000003`).
- Guard division by zero explicitly (percent-change with a zero base is `0.0`).

## Tests
- Test-first: a new behaviour lands as a failing test before the implementation.
- Use the stdlib `unittest` (no third-party test deps).
- Name tests after the acceptance criterion they cover (e.g. `test_ac3_...`).

## Docs
- A new architectural decision gets an ADR under `docs/adr/`.
- A new feature gets a spec under `specs/` with numbered acceptance criteria.
