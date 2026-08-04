"""Tests for summarize_series — written test-first, against specs/rate_summary.md.

Run with:  python3 -m unittest -v test_rate_summary
"""

import unittest

import exchange_rates as er


def _series(values):
    # Build oldest->newest points with dummy sequential dates.
    return [{"date": f"2026-08-{i + 1:02d}", "value": v} for i, v in enumerate(values)]


class TestSummarizeSeries(unittest.TestCase):
    def test_ac1_shape_has_exact_keys(self):
        s = er.summarize_series(_series([0.90, 0.92, 0.91]))
        self.assertEqual(
            set(s.keys()),
            {"high", "low", "average", "first", "latest", "change", "pct_change", "trend"},
        )

    def test_ac2_high_and_low(self):
        s = er.summarize_series(_series([0.90, 0.95, 0.88, 0.93]))
        self.assertEqual(s["high"], 0.95)
        self.assertEqual(s["low"], 0.88)

    def test_ac3_average_rounded_4dp(self):
        s = er.summarize_series(_series([0.90, 0.91, 0.92]))
        self.assertEqual(s["average"], 0.91)  # mean exactly 0.91

    def test_ac3_average_no_float_noise(self):
        s = er.summarize_series(_series([0.10, 0.20, 0.20]))
        # mean = 0.16666... -> rounded to 0.1667
        self.assertEqual(s["average"], 0.1667)

    def test_ac4_first_and_latest(self):
        s = er.summarize_series(_series([0.90, 0.95, 0.99]))
        self.assertEqual(s["first"], 0.90)
        self.assertEqual(s["latest"], 0.99)

    def test_ac5_change_rounded(self):
        s = er.summarize_series(_series([0.9000, 0.9912]))
        self.assertEqual(s["change"], 0.0912)

    def test_ac6_pct_change_rounded_2dp(self):
        s = er.summarize_series(_series([0.90, 0.99]))
        # (0.09 / 0.90) * 100 = 10.0
        self.assertEqual(s["pct_change"], 10.0)

    def test_ac6_pct_change_zero_first_no_division_error(self):
        s = er.summarize_series(_series([0.0, 0.5]))
        self.assertEqual(s["pct_change"], 0.0)

    def test_ac7_trend_up(self):
        self.assertEqual(er.summarize_series(_series([0.90, 0.95]))["trend"], "up")

    def test_ac7_trend_down(self):
        self.assertEqual(er.summarize_series(_series([0.95, 0.90]))["trend"], "down")

    def test_ac7_trend_flat(self):
        self.assertEqual(er.summarize_series(_series([0.90, 0.90]))["trend"], "flat")

    def test_ac8_single_point(self):
        s = er.summarize_series(_series([0.9123]))
        self.assertEqual(s["high"], 0.9123)
        self.assertEqual(s["low"], 0.9123)
        self.assertEqual(s["first"], 0.9123)
        self.assertEqual(s["latest"], 0.9123)
        self.assertEqual(s["average"], 0.9123)
        self.assertEqual(s["change"], 0.0)
        self.assertEqual(s["pct_change"], 0.0)
        self.assertEqual(s["trend"], "flat")

    def test_ac9_empty_raises_value_error(self):
        with self.assertRaises(ValueError):
            er.summarize_series([])


if __name__ == "__main__":
    unittest.main(verbosity=2)
