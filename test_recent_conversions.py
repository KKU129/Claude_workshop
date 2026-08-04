"""Tests for recent_conversions (see specs/recent_conversions.md).

Test-first: these cover the acceptance criteria AC1..AC6 and are named after
them. Pure, offline unittest — no network, no third-party deps.
"""

import unittest

from exchange_rates import recent_conversions


def _series(*values, start="2026-01-01"):
    """Build an oldest->newest series with sequential dates from ``start``."""
    from datetime import date, timedelta

    y, m, d = (int(x) for x in start.split("-"))
    base = date(y, m, d)
    return [
        {"date": (base + timedelta(days=i)).isoformat(), "value": v}
        for i, v in enumerate(values)
    ]


class RecentConversionsTests(unittest.TestCase):
    def test_ac1_shape_keys(self):
        rows = recent_conversions(_series(1.1, 1.2), amount=10)
        self.assertIsInstance(rows, list)
        for row in rows:
            self.assertEqual(set(row), {"date", "rate", "usd", "eur"})

    def test_ac2_newest_first(self):
        series = _series(1.0, 1.1, 1.2, start="2026-03-01")
        rows = recent_conversions(series, amount=1)
        dates = [r["date"] for r in rows]
        self.assertEqual(dates, ["2026-03-03", "2026-03-02", "2026-03-01"])

    def test_ac3_limit_caps_to_most_recent(self):
        series = _series(1.0, 1.1, 1.2, 1.3, 1.4)  # 5 days
        rows = recent_conversions(series, amount=1, limit=2)
        self.assertEqual(len(rows), 2)
        self.assertEqual([r["date"] for r in rows], ["2026-01-05", "2026-01-04"])

    def test_ac3_limit_default_is_seven(self):
        series = _series(*[1.0 + i * 0.1 for i in range(10)])  # 10 days
        rows = recent_conversions(series, amount=1)
        self.assertEqual(len(rows), 7)

    def test_ac3_fewer_than_limit_returns_all(self):
        series = _series(1.1, 1.2, 1.3)  # 3 days, default limit 7
        rows = recent_conversions(series, amount=1)
        self.assertEqual(len(rows), 3)

    def test_ac4_conversion_math(self):
        # AC4: eur is computed from the *rounded* rate, not the raw value, so
        # the shown EUR is internally consistent with the shown rate. This
        # value is chosen so raw vs rounded produce a different cent:
        #   raw:     1000 * 0.537647865 = 537.647... -> 537.65
        #   rounded: 1000 * 0.5376      = 537.60      (spec-correct)
        rows = recent_conversions(_series(0.537647865), amount=1000)
        row = rows[0]
        self.assertEqual(row["rate"], 0.5376)
        self.assertEqual(row["usd"], 1000.0)
        self.assertEqual(row["eur"], 537.60)

    def test_ac4_usd_is_float(self):
        row = recent_conversions(_series(1.1), amount=5)[0]
        self.assertIsInstance(row["usd"], float)
        self.assertEqual(row["usd"], 5.0)

    def test_ac5_empty_series_returns_empty_list(self):
        self.assertEqual(recent_conversions([], amount=10), [])

    def test_ac6_negative_amount_raises(self):
        with self.assertRaises(ValueError):
            recent_conversions(_series(1.1), amount=-1)

    def test_ac6_non_numeric_amount_raises(self):
        with self.assertRaises(ValueError):
            recent_conversions(_series(1.1), amount="ten")

    def test_ac6_bool_amount_raises(self):
        with self.assertRaises(ValueError):
            recent_conversions(_series(1.1), amount=True)

    def test_ac6_limit_below_one_raises(self):
        with self.assertRaises(ValueError):
            recent_conversions(_series(1.1), amount=10, limit=0)


if __name__ == "__main__":
    unittest.main()
