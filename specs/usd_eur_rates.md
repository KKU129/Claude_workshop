# Spec: USD → EUR 7-day rate core (`exchange_rates.py`)

## Goal
Provide the pure, offline-testable core logic behind the USD→EUR 7-day
dashboard: building the date range, parsing provider responses, a default
fallback series, the day-over-day delta, and assembling the final series.
Networking is injected (a `fetch_day` callable), so the module itself performs
no I/O and imports without side effects.

## Definitions
- A **point** is a dict `{"date": "YYYY-MM-DD", "value": <float>}`.
- Dates are ISO `YYYY-MM-DD` strings, ordered **oldest → newest**.
- "Today" is passed in as a `datetime.date` so tests are deterministic.

## Acceptance criteria

- **AC1 — `last_7_dates(today)`**: returns a list of exactly 7 ISO date
  strings, oldest → newest, inclusive of `today` (so `today - 6 … today`).

- **AC2 — `build_default_series(today)`**: returns 7 points for `last_7_dates`,
  values incrementing by `0.1` starting at `1.0` (i.e. `1.0, 1.1, … 1.6`).
  Values are rounded to at most 4 decimals so floating-point noise does not
  appear (e.g. exactly `1.3`, not `1.3000000000000003`).

- **AC3 — `parse_currency_api(payload, date)`**: reads
  `payload["usd"]["eur"]` (Currency API shape). Returns a point using
  `payload["date"]` when present, otherwise the passed `date`. Returns `None`
  if the value is missing or not a number.

- **AC4 — `parse_frankfurter(payload, date)`**: reads
  `payload["rates"]["EUR"]` (Frankfurter shape). Returns a point using
  `payload["date"]` when present, otherwise the passed `date`. Returns `None`
  if the value is missing or not a number.

- **AC5 — `build_series(dates, fetch_day)`**: calls `fetch_day(date)` for each
  date; `fetch_day` returns a point or `None`. Drops `None`s, de-duplicates by
  date (last value for a date wins), and returns points sorted oldest → newest.
  Raises `ValueError` if no point is resolved for any date.

- **AC6 — `compute_delta(prev_value, latest_value)`**: returns a tuple
  `(diff, pct)` where `diff = latest - prev` and `pct = diff / prev * 100`.
  When `prev_value == 0`, `pct` is `0.0` (no division by zero).

- **AC7 — no I/O on import**: importing the module performs no network calls;
  all fetching is done through the injected `fetch_day` callable.

## Out of scope
- HTTP/network implementation, retries, CLI, and the HTML dashboard itself.
- Currency pairs other than USD→EUR.
