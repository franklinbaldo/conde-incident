"""Regression checks for cumulative links without false domain reduction."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "formal" / "scripts"))
from check_cumulative_connections import validate  # noqa: E402

INPUT = ROOT / "research" / "constraints" / "ssr_1963_observable_graph.json"


class CumulativeConstraintGraphTests(unittest.TestCase):
    def setUp(self):
        self.graph = json.loads(INPUT.read_text(encoding="utf-8"))

    def test_all_table_cells_are_connected_without_premature_narrowing(self):
        out = validate(self.graph)
        self.assertEqual(out["input_observations"], 22)
        self.assertEqual(out["connected_observations"], 22)
        self.assertEqual(out["derived_connections_recorded"], 8)
        self.assertEqual(out["unique_source_families"], 2)
        self.assertEqual(out["constraints_activated"], 0)
        self.assertEqual(out["physical_domain_status"], "PENDING_CALIBRATION_NOT_DISCARDED")
        self.assertTrue(all(o["status"] == "CANDIDATE_NOT_ACTIVATED" for o in out["observations"]))

    def test_unit_conversion_is_explicit_but_epoch_remains_unknown(self):
        out = validate(self.graph)
        row = next(o for o in out["observations"] if o["observation"] == "SSR-1963-11-15-NORAD529-nodal_period")
        self.assertAlmostEqual(row["canonical_value"], 92.6 * 60)
        self.assertEqual(row["canonical_unit"], "s")
        self.assertIsNone(row["observed_at_utc"])
        self.assertIsNone(row["measurement_error"])

    def test_orphan_source_fails_closed(self):
        bad = copy.deepcopy(self.graph)
        bad["observations"][0]["source_id"] = "NONE"
        with self.assertRaisesRegex(ValueError, "orphan observation source"):
            validate(bad)

    def test_missing_epoch_cannot_be_silently_erased(self):
        bad = copy.deepcopy(self.graph)
        bad["observations"][0]["pending"].remove("observed_epoch")
        with self.assertRaisesRegex(ValueError, "missing epoch"):
            validate(bad)

    def test_unknown_error_cannot_be_silently_erased(self):
        bad = copy.deepcopy(self.graph)
        bad["observations"][0]["pending"].remove("error_interval")
        with self.assertRaisesRegex(ValueError, "unknown uncertainty"):
            validate(bad)

    def test_physical_activation_requires_external_validation(self):
        bad = copy.deepcopy(self.graph)
        bad["observations"][0]["constraint_status"] = "ACTIVE_HARD"
        with self.assertRaisesRegex(ValueError, "cannot activate"):
            validate(bad)

    def test_published_difference_is_not_a_measured_time_derivative(self):
        out = validate(self.graph)
        delta = next(d for d in out["derived_connections"] if d["id"] == "SSR-PUBLICATIONS-DELTA-529-nodal_period")
        self.assertAlmostEqual(delta["derived_arithmetic"], -0.4)
        self.assertIn("NOT a measured time derivative", delta["physical_interpretation"])

    def test_forged_delta_rejected(self):
        bad = copy.deepcopy(self.graph)
        bad["derived_connections"][0]["derived_arithmetic"] = 1234
        with self.assertRaisesRegex(ValueError, "invalid arithmetic"):
            validate(bad)

    def test_no_count_double_from_shared_upstream_tracking(self):
        out = validate(self.graph)
        self.assertEqual(len(self.graph["sources"]), 3)
        self.assertEqual(out["unique_source_families"], 2)
        self.assertEqual(out["upstream_tracking_families"], 1)

    def test_unknown_unit_fails(self):
        bad = copy.deepcopy(self.graph)
        bad["observations"][0]["unit"] = "furlongs"
        with self.assertRaisesRegex(ValueError, "unknown physical unit"):
            validate(bad)

    def test_c179_added_six_custodied_fields_and_numeric_bridge(self):
        out = validate(self.graph)
        self.assertEqual(out["physical_bridges_recorded"], 1)
        self.assertEqual(out["constraints_activated"], 0)
        bridge = out["physical_bridges"][0]
        self.assertEqual(bridge["source_occurrence"], "C179#1")
        self.assertEqual(bridge["element_epoch_utc"], "1963-10-27T14:40:16.132512Z")
        self.assertAlmostEqual(bridge["raan_rate_deg_per_day_first_order_j2_proxy"], -1.173124071, places=8)
        self.assertAlmostEqual(bridge["legacy_raan_delta_deg"], 85.6259, places=7)
        self.assertEqual(bridge["physical_domain"], "NOT_NARROWED_UNCALIBRATED_SOURCE")
        rows = [o for o in out["observations"] if o["source"] == "AFSPC-SECONDARY-528-1963-10-27"]
        self.assertEqual(len(rows), 6)
        self.assertTrue(all(row["element_epoch_utc"] == bridge["element_epoch_utc"] for row in rows))
        self.assertTrue(all(row["observed_at_utc"] is None for row in rows))
        self.assertEqual(len({row["independence_family"] for row in rows}), 1)

    def test_secondary_tle_changed_raan_without_changing_hash_is_rejected(self):
        bad = copy.deepcopy(self.graph)
        row = next(o for o in bad["observations"] if o["id"].endswith("NORAD528-raan"))
        row["value"] = 284.1520
        with self.assertRaisesRegex(ValueError, "C179 TLE value"):
            validate(bad)

    def test_legacy_unsourced_raan_must_not_become_historical_measurement(self):
        bad = copy.deepcopy(self.graph)
        bad["legacy_candidates"][0]["status"] = "PRIMARY_CONFIRMED"
        with self.assertRaisesRegex(ValueError, "legacy unsourced"):
            validate(bad)

    def test_element_epoch_is_not_instrumental_observation_epoch(self):
        bad = copy.deepcopy(self.graph)
        row = next(o for o in bad["observations"] if o["id"].endswith("NORAD528-mean_motion"))
        row["observed_at_utc"] = row["element_epoch_utc"]
        with self.assertRaisesRegex(ValueError, "C179 TLE value"):
            validate(bad)


if __name__ == "__main__":
    unittest.main()
