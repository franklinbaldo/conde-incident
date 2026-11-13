"""Adversarial tests of the custody/Lean/latent link, not a Conde weather fit."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from export_isd_caravelas_bridge import (
    REPORT, GRAPH, NMC, OBSERVABLE, OUT, build, render,
)


class BridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = [json.loads((ROOT / p).read_text())
                       for p in (REPORT, GRAPH, NMC, OBSERVABLE)]

    def make(self, index=None, change=None):
        docs = copy.deepcopy(self.sources)
        if index is not None:
            change(docs[index])
        return build(*docs, {})

    def test_real_72_rows_do_not_set_conde_winds(self):
        v = self.make()
        self.assertEqual(v["observations_at_caravelas"], 72)
        self.assertFalse(v["activation"])
        self.assertEqual(v["physical_domain_effect"], "THETA_UNCHANGED")
        self.assertIsNone(v["simulator_value"])
        self.assertIsNone(v["independent_physical_source_count"])
        self.assertIsNone(v["terminal_epoch_528"])
        self.assertEqual(len(v["graph_edges"]), 4)
        self.assertEqual(v["comparison_context"]["source_id"], "NOAA_IGRA_RECIFE_1963")

    def test_wrong_archive_hash(self):
        with self.assertRaises(ValueError):
            self.make(0, lambda d: d["source"].update(excerpt_sha256="0"*64))

    def test_wrong_station(self):
        with self.assertRaises(ValueError):
            self.make(1, lambda d: d["observation"].update(station_usaf="82900"))

    def test_false_conde_transfer(self):
        with self.assertRaises(ValueError):
            self.make(1, lambda d: d["edges"][1].update(type="OBSERVED_IN_CONDE"))

    def test_invented_instrument_uncertainty(self):
        with self.assertRaises(ValueError):
            self.make(0, lambda d: d["quality"].update(measurement_uncertainty=0.1))

    def test_promoted_conde_constraint(self):
        with self.assertRaises(ValueError):
            self.make(1, lambda d: d.update(active_conde_constraint=True))

    def test_phantom_ncar_observations(self):
        with self.assertRaises(ValueError):
            self.make(2, lambda d: d.update(numeric_observations_generated=9))

    def test_matrix_occurrence_swap(self):
        with self.assertRaises(ValueError):
            self.make(3, lambda d: next(x for x in d["edges"] if x["source_id"] ==
                "NOAA_IGRA_RECIFE_1963").update(matrix_occurrence="C179#1"))

    def test_false_recife_physical_activation(self):
        with self.assertRaises(ValueError):
            self.make(3, lambda d: next(x for x in d["edges"] if x["source_id"] ==
                "NOAA_IGRA_RECIFE_1963").update(activation=True))

    def test_export_and_lean_candidate_present(self):
        self.assertEqual(OUT.read_bytes(), render())
        lean = (ROOT / "formal/Conde1963/CaravelasCandidate.lean").read_text()
        self.assertIn("MET-ISD-19631107-09-CARAVELAS-01", lean)
        self.assertIn("CONNECTED_PENDING_SPATIOTEMPORAL_CALIBRATION", lean)
        self.assertIn("c6926a86150df982d13286285c17a70e4752cb1ce0ffe1d44ae5330be215a000", lean)
        self.assertLessEqual(OUT.stat().st_size, 20_000)


if __name__ == "__main__":
    unittest.main()
