"""G77: verified MODERN polygon sensitivity, never a 1963 impact constraint."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
from unittest import mock
import math
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import c241_modern_boundary_plane_g77 as g77  # noqa: E402


class ModernBoundaryG77(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = g77.payload(ROOT)
        cls.data = json.loads(cls.payload)

    def test_exact_byte_replay_and_nonhistorical_classification(self):
        self.assertEqual(
            self.payload,
            (ROOT / "research/statistics/c241_modern_boundary_plane_g77.json").read_bytes(),
        )
        obj = self.data
        self.assertEqual(obj["schema"], "conde.c241-modern-boundary-vertex-plane-sensitivity/v1")
        self.assertEqual(obj["historic_1963_boundary_status"], "NOT_ESTABLISHED")
        self.assertEqual(obj["modern_boundary_editions_only"], [2022, 2025])
        self.assertEqual(obj["surface_sampling"], "BOUNDARY_VERTICES_ONLY_NOT_AREA_ENVELOPE")
        self.assertEqual(obj["phase_constraint"], "NOT_EVALUATED")
        self.assertFalse(obj["active_constraint"])
        self.assertFalse(obj["posterior"])
        self.assertIsNone(obj["impact_probability"])
        self.assertIsNone(obj["observed_event_utc"])
        self.assertFalse(obj["clock_branch_resolved"])
        self.assertFalse(obj["geodesy_conversion_applied"])

    def test_hashes_are_actual_file_bytes_not_a_declared_manifest(self):
        for path, sha in self.data["source_sha256"].items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), sha)

    def test_all_pinned_vertices_and_scenario_range(self):
        self.assertEqual([r["branch"] for r in self.data["reports"]], list(g77.BRANCHES))
        for report in self.data["reports"]:
            self.assertEqual(report["norad"], 528)
            self.assertTrue(report["reference_modern_camera_crossing_utc"].startswith("1963-11-08T23:"))
            self.assertEqual(
                [x["vertices_sampled_excluding_closure"] for x in report["editions"]],
                [3302, 3259],
            )
            extrema = [e["boundary_vertex_shift_seconds"] for e in report["editions"]]
            for row in extrema:
                self.assertLess(row["minimum"], -20)
                self.assertGreater(row["maximum"], 50)
                self.assertGreater(row["maximum"] - row["minimum"], 80)
            # Two modern editions agree for these derived plane roots, which
            # still says nothing about boundaries or impact sites in 1963.
            self.assertLess(abs(extrema[0]["minimum"] - extrema[1]["minimum"]), 0.1)
            self.assertLess(abs(extrema[0]["maximum"] - extrema[1]["maximum"]), 0.1)

    def test_extreme_vertex_roots_against_independent_bisection(self):
        baseline, *_ = g77.g76.validate_inputs(ROOT)
        for branch, result in zip(g77.BRANCHES, self.data["reports"]):
            report = g77.g76.load(ROOT, g77.REPORT_PATH.format(branch))
            reference = g77.evening_root(report, baseline)
            origin = g77.g76.report_origin(report)
            for edition in result["editions"]:
                for edge in ("minimum", "maximum"):
                    lat, lon = edition["extremum_vertices_lat_lon_deg"][edge]
                    fn = lambda t: g77.plane.cross_km(
                        t, origin, report["da_dt_km_day"], lat, lon)
                    root = g77.plane.bisect(
                        fn, reference - timedelta(seconds=150),
                        reference + timedelta(seconds=150))
                    difference = (root - reference).total_seconds()
                    expected = edition["boundary_vertex_shift_seconds"][edge]
                    self.assertAlmostEqual(difference, expected, delta=0.12)

    def test_newton_rejects_tangencies_nonfinite_and_distant_roots(self):
        center = datetime(1963, 11, 8, tzinfo=timezone.utc)
        secs = lambda t: (t - center).total_seconds()
        root = g77.nearest_root(lambda t: secs(t) - 37.25, center)
        self.assertAlmostEqual(secs(root), 37.25, delta=0.0001)
        for fn in (lambda t: 1.0,
                   lambda t: float("nan"),
                   lambda t: secs(t) - 300):
            with self.assertRaises(ValueError):
                g77.nearest_root(fn, center)

    def test_historical_promotion_refused_even_if_reader_claims_it(self):
        original = g77.gis.read_snapshot(ROOT / g77.EDITION_PATH.format(2022))
        second = g77.gis.read_snapshot(ROOT / g77.EDITION_PATH.format(2025))
        mutated = deepcopy(original)
        mutated["metadata"]["valid_in_november_1963"] = "ESTABLISHED"
        with mock.patch.object(g77.gis, "read_snapshot", side_effect=[mutated, second]):
            with self.assertRaisesRegex(ValueError, "promoted to historical"):
                g77.generate(ROOT)

    def test_pinned_gis_source_rejects_one_changed_coordinate(self):
        original = g77.gis.read_snapshot(ROOT / g77.EDITION_PATH.format(2022))
        changed = deepcopy(original)
        changed["geometry"]["coordinates"][0][40][0] += 0.001
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "modified.json"
            path.write_text(json.dumps(changed), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "pinned source"):
                g77.gis.read_snapshot(path)


if __name__ == "__main__":
    unittest.main()
