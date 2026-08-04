# Spec: recent daily conversions (`recent_conversions`)

## Goal
Given an already-fetched USD→EUR series and a USD amount, produce the most
recent daily conversion rows — each day's rate and the converted EUR amount —
so the dashboard can show the "last N" conversions at a glance. Pure function,
no I/O: it operates only on the already-fetched series and stays import-safe and
network-free, consistent with the rest of the rate core.

## Definitions
- A **point** is `{"date": "YYYY-MM-DD", "value": <rate>}`, where `value` is the
  USD→EUR rate for that day.
- The input `points` is a list ordered **oldest → newest** (the series contract
  produced by `build_series`). Points are assumed well-formed.
- A **conversion row** is `{"date": <str>, "rate": <float>, "usd": <float>,
  "eur": <float>}`.

## API
`recent_conversions(points, amount, limit=7) -> list[dict]`

## Acceptance criteria

- **AC1 — shape**: returns a list of dicts, each with exactly these keys:
  `date`, `rate`, `usd`, `eur`.

- **AC2 — newest first**: rows are ordered **newest → oldest** (the most recent
  day, i.e. the last execution, comes first).

- **AC3 — limit**: returns at most `limit` rows — the most recent `limit` days.
  `limit` defaults to `7`. When the series has fewer than `limit` points, all of
  them are returned.

- **AC4 — conversion math**: for each row, `rate` is the day's `value` rounded to
  **4 decimals** (rate-value convention); `usd` equals the passed `amount` as a
  float; `eur = amount * rate` rounded to **2 decimals** (a currency amount, so
  cents — intentionally not the 4-decimal rate rule).

- **AC5 — empty series**: an empty `points` list returns `[]` (not an error).

- **AC6 — validation**: raises `ValueError` when `amount` is not a real number
  (bools excluded) or is negative, or when `limit < 1`.

## Out of scope
- Fetching/networking, HTML rendering/formatting, and any currency pair other
  than USD→EUR.
