"""Adversarial checks: one archived station, three derived days, zero Conde fit."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from export_isd_caravelas_vector_bridge import VECTORS, EDGES, SURFACE, OUT, LEAN, build, lean_block, render


class CaravelasVectorBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.docs = [json.loads((ROOT / p).read_text()) for p in (VECTORS, EDGES, SURFACE)]

    def mutate(self, index=None, fn=None):
        docs = copy.deepcopy(self.docs)
        if index is not None:
            fn(docs[index])
        return build(*docs, {})

    def test_connected_source_to_lean_to_simulator_but_not_conde(self):
        obj = self.mutate()
        self.assertEqual([d["u_millimetres_per_second"] for d in obj["derived_days"]],
                         [-2709, -2334, -2372])
        self.assertEqual([d["v_millimetres_per_second"] for d in obj["derived_days"]],
                         [-1702, -2382, -2812])
        self.assertEqual(obj["archive_rows"], 72)
        self.assertEqual(obj["independent_instrument_families"], 1)
        self.assertFalse(obj["independent_daily_measurements"])
        self.assertFalse(obj["activation"])
        self.assertIsNone(obj["simulator_value"])
        self.assertIsNone(obj["vertical_transfer_to_528"])
        self.assertEqual(obj["physical_domain_effect"], "THETA_UNCHANGED")
        self.assertEqual(obj["graph_edges"][-1]["type"], "PENDING_3D_TEMPORAL_SPATIAL_TRANSFER")
        self.assertIn("def caravelasDailyVectors", lean_block(obj))

    def test_wrong_archive_digest(self):
        with self.assertRaises(ValueError):
            self.mutate(0, lambda d: d["input"].update(archive_gz_sha256="0"*64))

    def test_false_independence_from_aggregated_days(self):
        with self.assertRaises(ValueError):
            self.mutate(0, lambda d: d["input"].update(same_instrument_family_for_all_hours=False))

    def test_false_instrument_sigma(self):
        with self.assertRaises(ValueError):
            self.mutate(1, lambda d: d.update(instrument_sigma_m_s=0.1))

    def test_false_geographic_transfer(self):
        with self.assertRaises(ValueError):
            self.mutate(1, lambda d: d.update(geographic_transfer_function="linear"))

    def test_wrong_vector_sign(self):
        with self.assertRaises(ValueError):
            self.mutate(0, lambda d: d["convention"].update(u_eastward="speed*sin(direction)"))

    def test_missing_day(self):
        with self.assertRaises(ValueError):
            self.mutate(0, lambda d: d["days"].pop("1963-11-08"))

    def test_original_occurrence_swap(self):
        with self.assertRaises(ValueError):
            self.mutate(2, lambda d: d.update(source_occurrence_id="C151#1"))

    def test_false_physical_activation(self):
        with self.assertRaises(ValueError):
            self.mutate(1, lambda d: d.update(active_conde_constraint=True))

    def test_changed_vector_magnitude(self):
        with self.assertRaises(ValueError):
            self.mutate(0, lambda d: d["days"]["1963-11-09"].update(mean_vector_magnitude_m_s=99.0))

    def test_source_locked_export_and_typed_lean_match(self):
        raw, lean = render()
        self.assertEqual(OUT.read_bytes(), raw)
        self.assertTrue(LEAN.read_text().endswith(lean))
        self.assertLess(len(raw), 20_000)


if __name__ == "__main__":
    unittest.main()
