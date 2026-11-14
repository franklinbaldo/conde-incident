"""R61 adverse tests: two printed days do not become two observations."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from c241_308_ssr_calendar_range_r61 import _expand_origin, report

MANIFEST = ROOT / "research/tle_custody/nasa_ssr_terminal_control_308_C241-L64.json"


def origin(low, v=1.0, epoch="1963-10-20T00:00:00+00:00"):
    return {"status": "COUNTERFACTUAL_INTERVAL_ONLY", "origin_utc": epoch,
            "decay_magnitude_km_day_LOCAL_PROXY": v,
            "required_H_km_UTC_DAY_COUNTERFACTUAL": [low, low+v]}


def baseline(records=None):
    records = records or [origin(10), origin(15, epoch="1963-10-21T00:00:00+00:00")]
    methods = {}
    for m in ("last_two", "median_three"):
        methods[m] = {"origins": copy.deepcopy(records),
                      "distinct_catalogue_origins": len(records),
                      "common_clock_24h": {"status": "NO_COMMON_H_FOR_ANY_SHIFT_IN_STRESS_WINDOW"}}
    return {"schema": "conde.c241-1963-archive-fixed-h-stress/v1",
            "design": {"clock": "SECONDARY_DAY_AS_HYPOTHETICAL_UTC_NOT_VERIFIED"},
            "inference": {"historical_mcmc": "NOT_RUN", "active_constraint_528": False},
            "cases": {"308": {"secondary_terminal_day": "1963-10-30",
                              "terminal_holdout_ready": False, "methods": methods}}}


def ssr():
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


class TwoDayRange(unittest.TestCase):
    def test_actual_manifest_keeps_identity_secondary(self):
        x = report(baseline(), ssr())
        self.assertEqual(x["printed_calendar_days_inclusive"],
                         ["1963-10-29", "1963-10-30"])
        self.assertIs(x["assumptions"]["actual_UTC_interval_known"], False)
        self.assertEqual(x["inference"]["calibrated_terminal_holdouts"], 0)
        self.assertEqual(x["inference"]["historical_mcmc"], "NOT_RUN")
        self.assertIsNone(x["inference"]["impact_probability"])

    def test_two_days_not_two_origins(self):
        x = report(baseline(), ssr())
        for m in x["methods"].values():
            self.assertEqual(m["distinct_origins"], 2)
            self.assertEqual(m["new_interval_H_km_conditional"], [[9.0, 11.0],
                                                                  [14.0, 16.0]])
            self.assertEqual(m["ssr_two_day_common_clock_24h"]["status"],
                             "NO_COMMON_H_FOR_ANY_SHIFT_IN_STRESS_WINDOW")
            self.assertEqual(m["ssr_two_day_independent_shift_1d"]["status"],
                             "INCOMPATIBLE_UNDER_INDEPENDENT_SHIFTS")

    def test_range_can_rescue_only_conditional_proxy(self):
        x = report(baseline([origin(10), origin(11.5, epoch="1963-10-21T00:00:00+00:00")]), ssr())
        self.assertEqual(x["methods"]["last_two"]["ssr_two_day_common_clock_24h"]["status"],
                         "FEASIBLE_ONLY_IN_ASSUMED_SHIFT_MODEL")
        self.assertIs(x["inference"]["active_constraint_528"], False)

    def test_cannot_promote_printed_norad(self):
        m = ssr()
        m["identity"]["nasa_explicitly_prints_308"] = True
        with self.assertRaisesRegex(ValueError, "crosswalk"):
            report(baseline(), m)

    def test_cannot_invent_terminal_utc(self):
        m = ssr()
        m["original_row"]["terminal_utc"] = "1963-10-30T00:00:00Z"
        with self.assertRaisesRegex(ValueError, "not timestamp"):
            report(baseline(), m)

    def test_cannot_invent_sigma(self):
        m = ssr()
        m["original_row"]["sigma_seconds"] = 1.0
        with self.assertRaisesRegex(ValueError, "not timestamp"):
            report(baseline(), m)

    def test_cannot_promote_second_sensor(self):
        m = ssr()
        m["source"]["individual_instrumental_observation"] = True
        with self.assertRaisesRegex(ValueError, "not an instrument"):
            report(baseline(), m)

    def test_bad_facsimile_sha_rejected(self):
        m = ssr()
        m["source"]["pdf_sha256"] = "0"*64
        with self.assertRaisesRegex(ValueError, "facsimile"):
            report(baseline(), m)

    def test_bad_range_rejected(self):
        m = ssr()
        m["original_row"]["calendar_range_start"] = "1963-10-28"
        with self.assertRaisesRegex(ValueError, "facsimile"):
            report(baseline(), m)

    def test_utc_clock_must_remain_unverified(self):
        b = baseline()
        b["design"]["clock"] = "VERIFIED_UTC"
        with self.assertRaisesRegex(ValueError, "clock"):
            report(b, ssr())

    def test_528_cannot_become_constrained(self):
        b = baseline()
        b["inference"]["active_constraint_528"] = True
        with self.assertRaisesRegex(ValueError, "unconstrained"):
            report(b, ssr())

    def test_no_duplicate_source_epochs(self):
        b = baseline()
        b["cases"]["308"]["methods"]["last_two"]["distinct_catalogue_origins"] = 3
        with self.assertRaisesRegex(ValueError, "duplicated origin"):
            report(b, ssr())

    def test_nonestimable_is_not_pass(self):
        b = baseline()
        b["cases"]["308"]["methods"]["last_two"]["origins"][0]["status"] = "NOT_ESTIMABLE"
        x = report(b, ssr())
        self.assertEqual(x["methods"]["last_two"]["ssr_two_day_common_clock_24h"]["status"],
                         "NOT_ESTIMABLE_ALL_CUTOFFS")
        self.assertEqual(x["methods"]["last_two"]["ssr_two_day_independent_shift_1d"]["status"],
                         "NOT_ESTIMABLE_ALL_CUTOFFS")

    def test_halfopen_origin_near_day_rejected(self):
        bad = origin(0.0, 1)
        bad["required_H_km_UTC_DAY_COUNTERFACTUAL"] = [0.0, 0.3]
        with self.assertRaisesRegex(ValueError, "too close"):
            _expand_origin(bad, 1)


if __name__ == "__main__":
    unittest.main()
