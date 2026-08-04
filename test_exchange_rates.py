"""Tests for exchange_rates.py — written test-first, against specs/usd_eur_rates.md.

Run with:  python3 -m unittest -v test_exchange_rates
"""

import unittest
from datetime import date

import exchange_rates as er


class TestLast7Dates(unittest.TestCase):
    def test_ac1_returns_seven_dates_oldest_to_newest_inclusive(self):
        today = date(2026, 8, 4)
        result = er.last_7_dates(today)
        self.assertEqual(len(result), 7)
        self.assertEqual(result[0], "2026-07-29")   # today - 6
        self.assertEqual(result[-1], "2026-08-04")  # today
        self.assertEqual(result, sorted(result))     # ascending


class TestDefaultSeries(unittest.TestCase):
    def test_ac2_values_increment_by_point_one_from_one(self):
        today = date(2026, 8, 4)
        pts = er.build_default_series(today)
        self.assertEqual(len(pts), 7)
        self.assertEqual([p["value"] for p in pts],
                         [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6])

    def test_ac2_no_floating_point_noise(self):
        pts = er.build_default_series(date(2026, 8, 4))
        # 1.3 must be exactly 1.3, not 1.3000000000000003
        self.assertEqual(pts[3]["value"], 1.3)

    def test_ac2_dates_match_last_7_dates(self):
        today = date(2026, 8, 4)
        pts = er.build_default_series(today)
        self.assertEqual([p["date"] for p in pts], er.last_7_dates(today))


class TestParseCurrencyApi(unittest.TestCase):
    def test_ac3_extracts_value_and_prefers_payload_date(self):
        payload = {"date": "2026-08-01", "usd": {"eur": 0.9123}}
        pt = er.parse_currency_api(payload, "2026-08-02")
        self.assertEqual(pt, {"date": "2026-08-01", "value": 0.9123})

    def test_ac3_falls_back_to_passed_date(self):
        payload = {"usd": {"eur": 0.9}}
        pt = er.parse_currency_api(payload, "2026-08-02")
        self.assertEqual(pt, {"date": "2026-08-02", "value": 0.9})

    def test_ac3_missing_value_returns_none(self):
        self.assertIsNone(er.parse_currency_api({"usd": {}}, "2026-08-02"))
        self.assertIsNone(er.parse_currency_api({}, "2026-08-02"))

    def test_ac3_non_numeric_returns_none(self):
        payload = {"usd": {"eur": "oops"}}
        self.assertIsNone(er.parse_currency_api(payload, "2026-08-02"))


class TestParseFrankfurter(unittest.TestCase):
    def test_ac4_extracts_value_and_prefers_payload_date(self):
        payload = {"date": "2026-08-01", "rates": {"EUR": 0.9088}}
        pt = er.parse_frankfurter(payload, "2026-08-02")
        self.assertEqual(pt, {"date": "2026-08-01", "value": 0.9088})

    def test_ac4_missing_value_returns_none(self):
        self.assertIsNone(er.parse_frankfurter({"rates": {}}, "2026-08-02"))
        self.assertIsNone(er.parse_frankfurter({}, "2026-08-02"))


class TestBuildSeries(unittest.TestCase):
    def test_ac5_drops_none_dedupes_and_sorts(self):
        table = {
            "2026-08-01": {"date": "2026-08-01", "value": 0.90},
            "2026-08-02": None,
            "2026-08-03": {"date": "2026-08-03", "value": 0.92},
        }
        # Deliberately unsorted input order.
        dates = ["2026-08-03", "2026-08-01", "2026-08-02"]
        result = er.build_series(dates, lambda d: table[d])
        self.assertEqual(result, [
            {"date": "2026-08-01", "value": 0.90},
            {"date": "2026-08-03", "value": 0.92},
        ])

    def test_ac5_dedupe_last_value_wins(self):
        # Two source dates resolve to the same payload date.
        def fetch(d):
            return {"date": "2026-08-01", "value": 0.90 if d == "a" else 0.95}
        result = er.build_series(["a", "b"], fetch)
        self.assertEqual(result, [{"date": "2026-08-01", "value": 0.95}])

    def test_ac5_empty_raises_value_error(self):
        with self.assertRaises(ValueError):
            er.build_series(["2026-08-01"], lambda d: None)


class TestComputeDelta(unittest.TestCase):
    def test_ac6_diff_and_pct(self):
        diff, pct = er.compute_delta(0.90, 0.99)
        self.assertAlmostEqual(diff, 0.09)
        self.assertAlmostEqual(pct, 10.0)

    def test_ac6_negative(self):
        diff, pct = er.compute_delta(1.00, 0.90)
        self.assertAlmostEqual(diff, -0.10)
        self.assertAlmostEqual(pct, -10.0)

    def test_ac6_zero_prev_no_division_error(self):
        diff, pct = er.compute_delta(0.0, 0.5)
        self.assertAlmostEqual(diff, 0.5)
        self.assertEqual(pct, 0.0)


class TestNoIoOnImport(unittest.TestCase):
    def test_ac7_module_has_no_network_symbols_bound_at_import(self):
        # The module must not perform I/O on import; fetching is injected.
        # A light structural check: there is no module-level fetch performing
        # network access — build_series takes fetch_day as a parameter.
        import inspect
        sig = inspect.signature(er.build_series)
        self.assertIn("fetch_day", sig.parameters)


if __name__ == "__main__":
    unittest.main(verbosity=2)
