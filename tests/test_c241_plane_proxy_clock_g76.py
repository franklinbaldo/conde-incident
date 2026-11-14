"""G76: test modern OSM proxies and unresolved FBIS branches against real archive."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import c241_plane_proxy_clock_g76 as m  # noqa: E402


class ProxyClockG76(unittest.TestCase):
    def test_replay_exact_output_and_no_inferred_event(self):
        generated = m.payload(ROOT)
        self.assertEqual(generated, (ROOT / "research/statistics/c241_plane_proxy_clock_g76.json").read_bytes())
        result = json.loads(generated)
        self.assertEqual(len(result["reports"]), 4)
        self.assertTrue(all(len(r["points"]) == 2 for r in result["reports"]))
        self.assertFalse(result["active_constraint"])
        self.assertFalse(result["posterior"])
        self.assertIsNone(result["impact_probability"])
        self.assertIsNone(result["reported_event_utc"])
        self.assertEqual(result["phase_constraint"], "NOT_EVALUATED")
        self.assertEqual(result["clock_branch_decision"], "UNRESOLVED")

    def test_clock_assumptions_both_preserved(self):
        result = m.generate(ROOT)
        self.assertEqual(len(result["clock_ordering_conditional_only"]), 8)
        for row in result["clock_ordering_conditional_only"]:
            self.assertFalse(row["orbit_exclusion_licensed"])
            self.assertGreater(abs(row["root_minus_broadcast_minutes"]), 0)
            if row["broadcast_assumption"] == "GMT":
                self.assertEqual(row["ordering_only"], "AFTER")
                self.assertGreater(row["root_minus_broadcast_minutes"], 0)
            elif row["broadcast_assumption"] == "RIO_LOCAL":
                self.assertEqual(row["ordering_only"], "BEFORE_OR_EQUAL")
                self.assertLess(row["root_minus_broadcast_minutes"], 0)
            else:
                self.fail("unknown clock assumption")

    def test_geographic_nearby_proxies_stay_near_camera(self):
        result = m.generate(ROOT)
        for report in result["reports"]:
            roots = [p["crossings"] for p in report["points"]]
            self.assertEqual(len(roots[0]), len(roots[1]))
            self.assertGreaterEqual(len(roots[0]), 7)
            for crossings in roots:
                for c in crossings:
                    self.assertLess(abs(c["shift_from_camera_seconds"]), 180)
                    self.assertLess(c["cross_track_km_at_camera_crossing"], 3)
                    self.assertIsInstance(c["within_UTC_day_scenario"], bool)
                    self.assertIsInstance(c["within_Bahia_day_scenario"], bool)
                    self.assertFalse(c["within_UTC_day_scenario"] and not c["within_Bahia_day_scenario"])

    def sandbox(self, root: Path):
        paths = (m.OSM, m.CLOCK, m.INDEX,
                 "research/geo/cgeo15_vila_matriz_2022_camera_points.json",
                 "research/geo/cgeo20_centro_vila_2020.json",
                 "research/geo/conde_ibge_2022_sirgas2000.json")
        paths += tuple("research/statistics/c241_plane_" + s + ".json" for s in m.REPORTS)
        for path in paths:
            target = root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / path, target)

    def mutate(self, path: Path, fn):
        data = json.loads(path.read_text(encoding="utf-8"))
        fn(data)
        path.write_text(json.dumps(data), encoding="utf-8")

    def test_reject_historical_identity_promotion(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.sandbox(root)
            self.mutate(root / m.OSM,
                        lambda d: d["historical_context"].__setitem__(
                            "modern_nodes_equate_to_cgeo20_historical_sites", True))
            with self.assertRaisesRegex(ValueError, "historical identity"):
                m.generate(root)

    def test_reject_fake_clock_verification(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.sandbox(root)
            self.mutate(root / m.CLOCK, lambda d: d.__setitem__("verification_status", "VERIFIED"))
            with self.assertRaisesRegex(ValueError, "clock contract"):
                m.generate(root)

    def test_reject_clock_shift_and_baseline_tamper(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.sandbox(root)
            self.mutate(root / m.CLOCK, lambda d: d["conditional_branches"]["GMT"].__setitem__(
                "broadcast_utc_if_assumption_holds", "1963-11-08T21:30Z"))
            with self.assertRaisesRegex(ValueError, "inconsistent"):
                m.generate(root)
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.sandbox(root)
            self.mutate(root / "research/statistics/c241_plane_528_constant_a.json",
                        lambda d: d["crossings"][0].__setitem__("crossing_utc", "1963-11-06T04:00:00Z"))
            with self.assertRaisesRegex(ValueError, "archived camera roots"):
                m.generate(root)

    def test_reject_edited_base_geographic_sha(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.sandbox(root)
            self.mutate(root / "research/geo/conde_ibge_2022_sirgas2000.json",
                        lambda d: d.__setitem__("untrusted", True))
            with self.assertRaisesRegex(ValueError, "SHA mismatch"):
                m.generate(root)


if __name__ == "__main__":
    unittest.main()
