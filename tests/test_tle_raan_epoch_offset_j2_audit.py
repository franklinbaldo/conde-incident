"""C241-T10: synthetic counterexamples; not historical tracking observations."""
import copy
import math
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from tle_raan_epoch_offset_j2_audit import (
    audit, conditional_epoch_offset_test, elements,
    j2_secular_node_rate_deg_per_day,
)
from legacy_528_fingerprint import LEGACY_LINE1, LEGACY_LINE2
from audit_norad_1963 import tle_epoch_utc

PAIR = ROOT / "research/tle_custody/mirror_528_1963-10-27.tle"
LINE1, LINE2 = PAIR.read_text(encoding="ascii").splitlines()
MIRROR = elements(LINE2)
LEGACY = elements(LEGACY_LINE2)


def synthetic_row(source_row=3017, epoch=None, raandeg=198.52609252929688):
    return {"source_row": source_row,
            "epoch_utc": epoch or tle_epoch_utc(LINE1),
            "fields": {"raan": raandeg}}


def diagnostic(legacy=None, mirror=None, legacy_epoch=None, mirror_epoch=None):
    return conditional_epoch_offset_test(
        legacy_epoch or tle_epoch_utc(LEGACY_LINE1),
        mirror_epoch or tle_epoch_utc(LINE1),
        legacy or LEGACY, mirror or MIRROR,
    )


class J2ConditionalRAANAuditTests(unittest.TestCase):
    def test_independent_literal_epochs_and_large_raan_gap(self):
        r = diagnostic()
        self.assertEqual(r["epoch_separation_microseconds"], 16132608)
        self.assertAlmostEqual(r["shortest_raan_difference_deg"], 85.6259)
        self.assertEqual(r["epoch_offset_only_j2_model"], "EXCLUDED_CONDITIONALLY")
        self.assertEqual(r["physical_1963_raan_origin"], "UNRESOLVED")

    def test_required_rate_dwarfs_first_order_proxy_without_claiming_fit(self):
        r = diagnostic()
        self.assertGreater(r["minimum_required_node_rate_deg_per_day"], 450000)
        self.assertLess(r["max_j2_proxy_drift_deg_during_offset"], 0.0003)
        self.assertAlmostEqual(
            r["j2_proxy_rates_deg_per_day"]["secondary_mirror"],
            -1.173124071, places=5)

    def test_very_short_offset_is_not_an_explanation_even_with_four_decimals(self):
        ep = tle_epoch_utc(LEGACY_LINE1)
        r = diagnostic(mirror_epoch=ep + timedelta(microseconds=864))
        self.assertEqual(r["epoch_offset_only_j2_model"], "EXCLUDED_CONDITIONALLY")

    def test_same_epoch_is_explicitly_not_a_divide_by_zero_inference(self):
        ep = tle_epoch_utc(LEGACY_LINE1)
        with self.assertRaisesRegex(ValueError, "no epoch offset"):
            diagnostic(legacy_epoch=ep, mirror_epoch=ep)

    def test_same_raan_across_offset_not_excluded(self):
        other = copy.deepcopy(MIRROR)
        other["raan_deg"] = LEGACY["raan_deg"]
        r = diagnostic(mirror=other)
        self.assertEqual(r["shortest_raan_difference_deg"], 0)
        self.assertEqual(r["epoch_offset_only_j2_model"], "NOT_EXCLUDED_BY_THIS_BOUND")

    def test_shortest_circular_arc_not_naive_358_degrees(self):
        a, b = copy.deepcopy(LEGACY), copy.deepcopy(MIRROR)
        a["raan_deg"] = 359
        b["raan_deg"] = 1
        self.assertAlmostEqual(diagnostic(legacy=a, mirror=b)[
            "shortest_raan_difference_deg"], 2)

    def test_j2_rate_changes_sign_with_retrograde_inclination(self):
        pro = j2_secular_node_rate_deg_per_day(81.8615, 0.0017147, 15.74901460)
        retro = j2_secular_node_rate_deg_per_day(180 - 81.8615, 0.0017147, 15.74901460)
        self.assertAlmostEqual(pro, -retro, places=12)

    def test_invalid_model_inputs_fail_closed(self):
        for args in [
            (float("nan"), 0.0, 15.7), (81.0, 1.0, 15.7),
            (81.0, -0.1, 15.7), (81.0, 0.1, 0),
            (181, 0.0, 15.7), (81, 0, 30),
        ]:
            with self.subTest(args=args), self.assertRaisesRegex(ValueError, "J2 proxy"):
                j2_secular_node_rate_deg_per_day(*args)

    def test_naive_epoch_is_not_silently_assumed_utc(self):
        with self.assertRaisesRegex(ValueError, "UTC"):
            diagnostic(mirror_epoch=datetime(1963, 10, 27, 14, 40, 16))

    def test_same_epoch_secondary_row_required(self):
        with self.assertRaisesRegex(ValueError, "same-epoch"):
            audit([synthetic_row(epoch=tle_epoch_utc(LINE1) + timedelta(seconds=3))],
                  "SYNTHETIC", PAIR, expected_count=None)
        with self.assertRaisesRegex(ValueError, "same-epoch"):
            audit([synthetic_row(), synthetic_row(source_row=3018)],
                  "SYNTHETIC", PAIR, expected_count=None)

    def test_secondary_same_epoch_must_match_198_not_284(self):
        with self.assertRaisesRegex(ValueError, "RAAN differs"):
            audit([synthetic_row(raandeg=284.1520)],
                  "SYNTHETIC", PAIR, expected_count=None)

    def test_pinned_pair_hash_and_counts(self):
        with self.assertRaisesRegex(ValueError, "count"):
            audit([synthetic_row()], "SYNTHETIC", PAIR, expected_count=45)
        r = audit([synthetic_row()], "SYNTHETIC", PAIR, expected_count=None)
        self.assertEqual(r["same_epoch_numeric_source_row"], 3017)
        self.assertEqual(r["lean_4_35_physical_restriction"],
                         "NOT_PROMOTED_NO_PRIMARY_FRAME_OR_ERRORS")
        self.assertEqual(r["reentry_and_conde"], "INDETERMINATE")
        self.assertEqual(r["source"]["primary_norad_source"], "NOT_RECOVERED")


if __name__ == "__main__":
    unittest.main()
