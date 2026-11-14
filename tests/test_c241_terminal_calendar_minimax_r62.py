"""R62: two printed days are NOT a calibrated 48-hour UTC event."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from c241_terminal_calendar_minimax_r62 import _conditional_window, _day, report

MANIFEST = ROOT / "research/tle_custody/nasa_ssr_terminal_control_308_C241-L64.json"


def baseline():
    return {
        "schema": "conde.c241-1963-archive-fixed-h-stress/v1",
        "design": {"clock": "SECONDARY_DAY_AS_HYPOTHETICAL_UTC_NOT_VERIFIED"},
        "inference": {"historical_mcmc": "NOT_RUN", "active_constraint_528": False},
        "cases": {"308": {"secondary_terminal_day": "1963-10-30",
                          "terminal_holdout_ready": False}},
    }


def ssr():
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


class CalendarSetIdentification(unittest.TestCase):
    def test_source_has_not_been_promoted(self):
        x = report(baseline(), ssr())
        self.assertEqual(x["subject"], "NORAD_308_BY_SECONDARY_CROSSWALK_ONLY")
        self.assertIs(x["design"]["actual_terminal_utc_semantics_known"], False)
        self.assertEqual(x["design"]["source_independent_instrument_count"], 0)
        self.assertIs(x["inference"]["active_constraint_528"], False)
        self.assertIsNone(x["inference"]["terminal_sigma_hours"])
        self.assertEqual(x["inference"]["historical_mcmc"], "NOT_RUN")

    def test_calendar_minimax_arithmetic_exact(self):
        windows = report(baseline(), ssr())["conditional_windows"]
        self.assertEqual(windows["nasa_2day_print"]["hypothetical_width_hours"], 48)
        self.assertEqual(windows["nasa_2day_print"][
            "best_possible_worst_case_point_error_hours_IF_UTC"], 24)
        self.assertEqual(windows["secondary_1day_lead"]["hypothetical_width_hours"], 24)
        self.assertEqual(windows["secondary_1day_lead"][
            "best_possible_worst_case_point_error_hours_IF_UTC"], 12)
        self.assertEqual(windows["nasa_2day_print"]["begin_utc_IF_UTC_DAY_HYPOTHESIS"],
                         "1963-10-29T00:00:00Z")
        self.assertEqual(windows["nasa_2day_print"]["end_utc_exclusive_IF_UTC_DAY_HYPOTHESIS"],
                         "1963-10-31T00:00:00Z")
        for w in windows.values():
            self.assertIs(w["historical_utc_bound"], False)
            self.assertIs(w["instrumentally_observed_interval"], False)

    def test_one_day_not_independent_instrument(self):
        m = ssr()
        m["source"]["individual_instrumental_observation"] = True
        with self.assertRaisesRegex(ValueError, "lineage"):
            report(baseline(), m)

    def test_fake_nasa_satcat_rejected(self):
        m = ssr()
        m["identity"]["nasa_explicitly_prints_308"] = True
        with self.assertRaisesRegex(ValueError, "secondary"):
            report(baseline(), m)

    def test_fake_terminal_utc_rejected(self):
        m = ssr()
        m["original_row"]["terminal_utc"] = "1963-10-30T15:00:00Z"
        with self.assertRaisesRegex(ValueError, "not terminal"):
            report(baseline(), m)

    def test_fake_sensor_sigma_rejected(self):
        for field, value in (("sensor", "radar"), ("sigma_seconds", 4),
                             ("station", "unknown")):
            m = ssr()
            m["original_row"][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "not terminal"):
                report(baseline(), m)

    def test_changed_primary_sha_rejected(self):
        m = ssr()
        m["source"]["pdf_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "custody"):
            report(baseline(), m)

    def test_changed_printed_range_rejected(self):
        m = ssr()
        m["original_row"]["calendar_range_start"] = "1963-10-28"
        with self.assertRaisesRegex(ValueError, "drift"):
            report(baseline(), m)

    def test_predicted_utc_clock_still_unverified(self):
        b = baseline()
        b["design"]["clock"] = "UTC_VERIFIED"
        with self.assertRaisesRegex(ValueError, "clock"):
            report(b, ssr())

    def test_unearned_holdout_rejected(self):
        b = baseline()
        b["cases"]["308"]["terminal_holdout_ready"] = True
        with self.assertRaisesRegex(ValueError, "not calibrated"):
            report(b, ssr())

    def test_unearned_posterior_rejected(self):
        b = baseline()
        b["inference"]["historical_mcmc"] = "PASS"
        with self.assertRaisesRegex(ValueError, "posterior"):
            report(b, ssr())

    def test_bad_calendar_day_and_half_open_interval(self):
        with self.assertRaisesRegex(ValueError, "calendar"):
            _day("1963-13-30")
        self.assertEqual(_day("1963-10-30").isoformat(), "1963-10-30")
        with self.assertRaisesRegex(ValueError, "reversed"):
            _conditional_window(_day("1963-10-30"), _day("1963-10-29"), "bad")
        with self.assertRaisesRegex(ValueError, "unbounded"):
            _conditional_window(_day("1963-10-29"), _day("1963-11-05"), "bad")

    def test_source_missing_rejected(self):
        m = ssr()
        m.pop("source")
        with self.assertRaises((ValueError, KeyError)):
            report(baseline(), m)


if __name__ == "__main__":
    unittest.main()
