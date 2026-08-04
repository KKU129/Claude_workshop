# Spec: 7-day series summary (`summarize_series`)

## Goal
Given an already-fetched USD→EUR series, compute the headline statistics the
dashboard needs in one pass: high, low, average, first/latest values, absolute
and percent change over the window, and a trend label. Pure function, no I/O —
follows `docs/adr/0001-pure-rate-core.md`.

## Definitions
- A **point** is `{"date": "YYYY-MM-DD", "value": <float>}`.
- The input `points` is a list ordered **oldest → newest**.

## API
`summarize_series(points) -> dict`

## Acceptance criteria

- **AC1 — shape**: returns a dict with exactly these keys: `high`, `low`,
  `average`, `first`, `latest`, `change`, `pct_change`, `trend`.

- **AC2 — high / low**: `high` is the maximum `value` in `points`; `low` is the
  minimum.

- **AC3 — average**: arithmetic mean of the values, rounded to 4 decimals.

- **AC4 — first / latest**: `first` is the value of the oldest point (index 0);
  `latest` is the value of the newest point (last index).

- **AC5 — change**: `change = latest - first`, rounded to 4 decimals.

- **AC6 — pct_change**: `pct_change = change / first * 100`, rounded to 2
  decimals. When `first == 0`, `pct_change` is `0.0` (no division by zero).

- **AC7 — trend**: `"up"` when `change > 0`, `"down"` when `change < 0`, and
  `"flat"` when `abs(change) < 1e-9`.

- **AC8 — single point**: for a one-element series, `high == low == first ==
  latest == average`, `change == 0.0`, `pct_change == 0.0`, `trend == "flat"`.

- **AC9 — empty input**: raises `ValueError`.

## Out of scope
- Fetching/networking, formatting for display, and any currency pair other than
  USD→EUR.
