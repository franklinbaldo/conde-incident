"""G78: exact modern CONDER/OSM plane-source comparison, no historical inference."""
from __future__ import annotations
from copy import deepcopy
from datetime import timedelta
import hashlib
import json
from pathlib import Path
import sys
from unittest import TestCase, main, mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import c241_conder_seat_plane_g78 as g78  # noqa: E402


class ConditionalConderG78(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = g78.payload(ROOT)
        cls.data = json.loads(cls.raw)

    def test_byte_replay_and_source_hashes(self):
        self.assertEqual(self.raw,
                         (ROOT/"research/statistics/c241_conder_seat_plane_g78.json").read_bytes())
        for path, digest in self.data["source_sha256"].items():
            self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(), digest)

    def test_modern_proxies_are_not_historical_or_independent_measurements(self):
        obj = self.data
        self.assertEqual(obj["schema"], "conde.c241-modern-conder-seat-plane-sensitivity/v1")
        self.assertEqual(obj["official_source_role"], "CONDER_PRESENT_DAY_SEAT_PROXY_ONLY")
        self.assertIsNone(obj["source_observation_epoch"])
        self.assertIsNone(obj["historical_1963_site"])
        self.assertIsNone(obj["point_position_accuracy_m"])
        self.assertFalse(obj["independent_instrumental_measurements"])
        self.assertFalse(obj["active_constraint"])
        self.assertFalse(obj["posterior"])
        self.assertIsNone(obj["impact_probability"])
        self.assertEqual(obj["orbital_phase"], "NOT_EVALUATED")
        self.assertFalse(obj["broadcast_is_observed_event_time"])
        self.assertEqual(obj["clock_branch"], "UNRESOLVED")

    def test_modern_coordinates_change_root_without_phase_claim(self):
        self.assertAlmostEqual(self.data["distance_between_modern_proxies_m"],
                               751.891919, delta=1e-6)
        self.assertEqual([row["branch"] for row in self.data["results"]], list(g78.BRANCHES))
        for row in self.data["results"]:
            self.assertEqual(row["norad"], 528)
            self.assertGreater(abs(row["official_minus_osm_seconds"]), 0.1)
            self.assertLess(abs(row["official_minus_osm_seconds"]), 180)
            self.assertAlmostEqual(
                row["official_minus_osm_seconds"],
                row["official_minus_camera_seconds"]-row["osm_minus_camera_seconds"],
                delta=0.002)
            self.assertGreater(row["conder_cross_track_km_at_osm_root"], 0)

    def test_independent_bisection_confirms_official_roots(self):
        baseline, *_ = g78.g76.validate_inputs(ROOT)
        point = g78.g76.load(ROOT, g78.CONDER)["point"]
        for row in self.data["results"]:
            record = g78.g76.load(ROOT, g78.g77.REPORT_PATH.format(row["branch"]))
            center = g78.g77.evening_root(record, baseline)
            origin = g78.g76.report_origin(record)
            fn = lambda t: g78.plane.cross_km(
                t, origin, record["da_dt_km_day"], point["latitude"], point["longitude"])
            result = g78.plane.bisect(fn, center-timedelta(seconds=150),
                                     center+timedelta(seconds=150))
            archived = g78.g76.parse_utc(row["conder_sede_root_utc"])
            self.assertAlmostEqual((result-archived).total_seconds(), 0, delta=0.12)

    def test_false_historical_bridge_is_rejected(self):
        original = g78.g76.load(ROOT, g78.CONDER)
        forged = deepcopy(original)
        forged["historical_guards"]["modern_sede_is_historical_center"] = True
        load = g78.g76.load
        def reader(repo, path):
            return forged if path == g78.CONDER else load(repo, path)
        with mock.patch.object(g78.g76, "load", side_effect=reader):
            with self.assertRaisesRegex(ValueError, "historical"):
                g78.generate(ROOT)

    def test_forged_coordinate_is_rejected(self):
        original = g78.g76.load(ROOT, g78.CONDER)
        forged = deepcopy(original)
        forged["point"]["longitude"] += 0.01
        load = g78.g76.load
        def reader(repo, path):
            return forged if path == g78.CONDER else load(repo, path)
        with mock.patch.object(g78.g76, "load", side_effect=reader):
            with self.assertRaisesRegex(ValueError, "unverified CONDER point"):
                g78.generate(ROOT)


if __name__ == "__main__":
    main()
