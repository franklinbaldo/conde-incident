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
        self.assertEqual(out["input_observations"], 16)
        self.assertEqual(out["connected_observations"], 16)
        self.assertEqual(out["derived_connections_recorded"], 8)
        self.assertEqual(out["unique_source_families"], 1)
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
        self.assertEqual(len(self.graph["sources"]), 2)
        self.assertEqual(out["unique_source_families"], 1)

    def test_unknown_unit_fails(self):
        bad = copy.deepcopy(self.graph)
        bad["observations"][0]["unit"] = "furlongs"
        with self.assertRaisesRegex(ValueError, "unknown physical unit"):
            validate(bad)

    def test_different_reported_units_cannot_be_subtracted_as_same_unit(self):
        bad = copy.deepcopy(self.graph)
        # Both units are individually permitted. Only the cross-row comparison is forged.
        other = bad["derived_connections"][0]["inputs"][1]
        next(o for o in bad["observations"] if o["id"] == other)["unit"] = "km"
        with self.assertRaisesRegex(ValueError, "mixed units in derived comparison"):
            validate(bad)

    def test_repeated_derived_id_cannot_inflate_connection_count(self):
        bad = copy.deepcopy(self.graph)
        bad["derived_connections"].append(copy.deepcopy(bad["derived_connections"][0]))
        with self.assertRaisesRegex(ValueError, "duplicate or invalid derived edge ID"):
            validate(bad)

    def test_new_id_for_same_comparison_is_still_duplicate(self):
        bad = copy.deepcopy(self.graph)
        clone = copy.deepcopy(bad["derived_connections"][0])
        clone["id"] = "FORGED-DERIVED-NUMBER-TWO"
        bad["derived_connections"].append(clone)
        with self.assertRaisesRegex(ValueError, "duplicate derived observation pair"):
            validate(bad)

    def test_reversed_difference_does_not_count_as_independent_edge(self):
        bad = copy.deepcopy(self.graph)
        clone = copy.deepcopy(bad["derived_connections"][0])
        clone["id"] = "FORGED-DERIVED-REVERSE"
        clone["inputs"].reverse()
        clone["derived_arithmetic"] = -clone["derived_arithmetic"]
        bad["derived_connections"].append(clone)
        with self.assertRaisesRegex(ValueError, "duplicate derived observation pair"):
            validate(bad)

    def test_nan_derived_arithmetic_cannot_bypass_absolute_error_check(self):
        bad = copy.deepcopy(self.graph)
        bad["derived_connections"][0]["derived_arithmetic"] = float("nan")
        with self.assertRaisesRegex(ValueError, "non-finite or nonnumeric derived arithmetic"):
            validate(bad)

    def test_boolean_zero_is_not_numeric_derived_evidence(self):
        bad = copy.deepcopy(self.graph)
        zero = next(e for e in bad["derived_connections"] if e["id"].endswith("527-inclination"))
        self.assertEqual(zero["derived_arithmetic"], 0)
        zero["derived_arithmetic"] = False
        with self.assertRaisesRegex(ValueError, "non-finite or nonnumeric derived arithmetic"):
            validate(bad)


if __name__ == "__main__":
    unittest.main()
