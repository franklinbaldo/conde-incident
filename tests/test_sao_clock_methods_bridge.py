"""P14/SR266 documentary dependence; -O-safe adversarial cases."""
import copy
from pathlib import Path
import sys
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import export_sao_clock_methods_bridge as bridge

class SaoClockMethodBridge(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = bridge.load()

    def test_site_determinism(self):
        self.assertEqual(bridge.OUT.read_bytes(), bridge.render())

    def test_two_pinned_distinct_historical_publications(self):
        d = bridge.build(self.sources)
        self.assertEqual(["C241-L59", "C241-L60"], [s["occurrence_id"] for s in d["sources"]])
        self.assertNotEqual(d["sources"][0]["original_pdf_sha256"],
                            d["sources"][1]["original_pdf_sha256"])
        self.assertEqual(5140, d["published_target_scope"]["P14_selected_rows"])
        self.assertTrue(d["published_target_scope"]["not_in_catalogue_is_not_global_absence"])
        self.assertIsNone(d["global_unknown_528_observation_count"])

    def test_conditional_clock_not_utc_or_extrapolated(self):
        d = bridge.build(self.sources)
        self.assertEqual(2.292725, d["time_model"]["P14"]["A1_minus_WWV_emitted_seconds_at_mjd_38030"])
        self.assertEqual(38334, d["time_model"]["P14"]["valid_mjd_upper_exclusive"])
        self.assertFalse(d["time_model"]["transfer_between_series_authorized"])
        self.assertTrue(d["time_model"]["P14"]["not_a_UTC_conversion"])

    def test_no_physical_promotion_or_duplicated_sensor(self):
        d = bridge.build(self.sources)
        self.assertFalse(d["activation"])
        self.assertEqual("THETA_UNCHANGED", d["physical_domain_effect"])
        self.assertEqual("CANDIDATE_ONLY_NOT_COMPILED", d["lean_status"])
        self.assertEqual(0, d["new_activated_physical_constraints"])
        self.assertEqual(0, d["independent_instrumental_measurements_added_for_528"])
        self.assertTrue(all(not e["activation"] for e in d["graph"]))
        self.assertTrue(all(x["value"] is None and not x["activation"] for x in d["latents"] + d["simulator_parameters"]))
        self.assertEqual(27, len(d["graph"]))

    def mutant(self, sid, path, value):
        d = copy.deepcopy(self.sources)
        target = d[sid]
        for k in path[:-1]:
            target = target[k]
        target[path[-1]] = value
        with self.assertRaises(ValueError):
            bridge.build(d)

    def test_reject_p14_fabricated_target(self):
        self.mutant("C241-L59", ["observations_scope", "norad_527_528_529_in_list"], True)

    def test_reject_p14_clock_conflation(self):
        self.mutant("C241-L59", ["measurement_method_context_only", "time_scale"], "UTC")

    def test_reject_p14_station_datum_conflation(self):
        self.mutant("C241-L59", ["measurement_method_context_only", "station_geodetic_reference"], "WGS84")

    def test_reject_p14_fake_528_covariance(self):
        self.mutant("C241-L59", ["target_527_528_529", "covariance"], [[1]])

    def test_reject_sr266_fake_528_identity(self):
        self.mutant("C241-L60", ["published_dataset", "includes_1963_003"], True)

    def test_reject_sr266_independence(self):
        self.mutant("C241-L60", ["published_dataset", "independence_policy"], "INDEPENDENT")

    def test_reject_sr266_time_scale(self):
        self.mutant("C241-L60", ["published_dataset", "time_scale"], "UTC")

    def test_reject_duplicate_json_keys(self):
        with self.assertRaisesRegex(ValueError, "duplicate JSON"):
            bridge.no_duplicate_keys([("x", 1), ("x", 2)])

    def test_both_manifests_are_hash_locked(self):
        for sid, (name, _) in bridge.SOURCES.items():
            with self.subTest(sid=sid), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                for path, _digest in bridge.SOURCES.values():
                    out = root / path
                    out.parent.mkdir(parents=True, exist_ok=True)
                    out.write_bytes((ROOT / path).read_bytes())
                (root / name).write_bytes((root / name).read_bytes() + b" ")
                with self.assertRaisesRegex(ValueError, "SHA drift"):
                    bridge.load(root)

if __name__ == "__main__":
    unittest.main()
