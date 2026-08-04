"""USD -> EUR 7-day rate core logic.

Pure, offline-testable helpers behind the USD->EUR dashboard. Networking is
injected via a ``fetch_day`` callable, so this module performs no I/O and
imports without side effects. See specs/usd_eur_rates.md for acceptance
criteria.
"""

from datetime import date, timedelta
from numbers import Real
from typing import Callable, Dict, List, Optional

Point = Dict[str, object]  # {"date": "YYYY-MM-DD", "value": float}

_DAYS = 7


def last_7_dates(today: date) -> List[str]:
    """AC1: 7 ISO dates, oldest -> newest, inclusive of ``today``."""
    return [(today - timedelta(days=i)).isoformat() for i in range(_DAYS - 1, -1, -1)]


def build_default_series(today: date) -> List[Point]:
    """AC2: default fallback series, values 1.0, 1.1, ... 1.6 (step 0.1)."""
    return [
        {"date": d, "value": round(1.0 + i * 0.1, 4)}
        for i, d in enumerate(last_7_dates(today))
    ]


def _numeric_point(value: object, payload_date: object, fallback_date: str) -> Optional[Point]:
    """Build a point if ``value`` is a real number (bool excluded), else None."""
    if isinstance(value, bool) or not isinstance(value, Real):
        return None
    point_date = payload_date if isinstance(payload_date, str) and payload_date else fallback_date
    return {"date": point_date, "value": float(value)}


def parse_currency_api(payload: dict, date_str: str) -> Optional[Point]:
    """AC3: extract ``payload['usd']['eur']`` (Currency API shape)."""
    value = (payload.get("usd") or {}).get("eur") if isinstance(payload, dict) else None
    return _numeric_point(value, payload.get("date") if isinstance(payload, dict) else None, date_str)


def parse_frankfurter(payload: dict, date_str: str) -> Optional[Point]:
    """AC4: extract ``payload['rates']['EUR']`` (Frankfurter shape)."""
    value = (payload.get("rates") or {}).get("EUR") if isinstance(payload, dict) else None
    return _numeric_point(value, payload.get("date") if isinstance(payload, dict) else None, date_str)


def build_series(dates: List[str], fetch_day: Callable[[str], Optional[Point]]) -> List[Point]:
    """AC5: fetch each date, drop Nones, dedupe by date (last wins), sort asc.

    Raises ValueError if no date resolves to a point.
    """
    by_date: Dict[str, float] = {}
    for d in dates:
        point = fetch_day(d)
        if point is None:
            continue
        by_date[point["date"]] = point["value"]

    if not by_date:
        raise ValueError("No rate data resolved for any date in the range")

    return [{"date": d, "value": by_date[d]} for d in sorted(by_date)]


def compute_delta(prev_value: float, latest_value: float):
    """AC6: (diff, pct) day-over-day change; pct is 0.0 when prev is 0."""
    diff = latest_value - prev_value
    pct = (diff / prev_value * 100) if prev_value else 0.0
    return diff, pct


def recent_conversions(points: List[Point], amount: float, limit: int = 7) -> List[Dict[str, object]]:
    """Recent daily USD->EUR conversion rows (see specs/recent_conversions.md).

    ``points`` is ordered oldest -> newest; returns the most recent ``limit``
    days as rows ordered newest -> oldest. Each row converts ``amount`` USD to
    EUR at that day's rate.
    """
    if limit < 1:  # AC6
        raise ValueError("limit must be at least 1")
    if isinstance(amount, bool) or not isinstance(amount, Real) or amount < 0:  # AC6
        raise ValueError("amount must be a non-negative number")

    amount = float(amount)
    recent = list(reversed(points[-limit:]))  # AC2/AC3: most recent first
    rows = []
    for p in recent:
        rate = round(float(p["value"]), 4)  # AC4: rate value -> 4 decimals
        rows.append({
            "date": p["date"],
            "rate": rate,
            "usd": amount,
            "eur": round(amount * rate, 2),  # AC4: convert via the shown rate -> cents
        })
    return rows
