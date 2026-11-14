"""Adversarial tests for L68 October snapshot and L67 cross-edition dependency graph."""
from __future__ import annotations

import copy
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import export_omega_snapshot_date_genealogy as bridge


class OmegaDependencyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parents = bridge.load()

    def case(self):
        return bridge.build(copy.deepcopy(self.parents))

    def test_export_byte_identical(self):
        self.assertEqual(bridge.OUT.read_bytes(), bridge.render())

    def test_source_hashes_locked(self):
        self.assertEqual([v[1] for v in bridge.INPUTS.values()],
                         [x["sha256"] for x in self.case()["sources"]])

    def test_20_edges_all_documentary(self):
        p = self.case()
        self.assertEqual(20, len(p["graph"]))
        for e in p["graph"]:
            self.assertTrue(e["documentary_only"])
            self.assertFalse(e["activation"])

    def test_october_report_cutoff_not_sensor_epoch(self):
        o = self.case()["october_catalogue"]
        self.assertEqual("1963-10-15T12:00:00Z", o["report_as_of_utc"])
        self.assertFalse(o["report_cutoff_is_observation_epoch"])
        self.assertIsNone(o["instrumental_observation_epoch_utc"])
        self.assertEqual("89.7", o["catalogued_elements"]["nodal_period_minutes"])

    def test_three_relabelings_are_not_identity_proofs(self):
        p = self.case()
        self.assertEqual([308, 310, 314],
                         [x["retrospective_catalog_number"] for x in p["date_signatures"]])
        self.assertEqual(["OMEGA 2", "OMEGA 3", "A-ALPHA 5"],
                         [x["retrospective_name"] for x in p["date_signatures"]])
        self.assertIsNone(p["october_catalogue"]["identity_norad_308"])

    def test_all_simulator_and_lean_gates_closed(self):
        p = self.case()
        self.assertEqual("THETA_UNCHANGED", p["physical_domain_effect"])
        self.assertEqual("NOT_RUN", p["historical_mcmc"])
        self.assertFalse(p["activation"])
        for x in p["simulator_parameters"]:
            self.assertIsNone(x["value"])
            self.assertFalse(x["activation"])
        self.assertFalse(p["lean_candidates"][0]["activation"])

    def test_documentary_facsimile_count_not_sensor_count(self):
        i = self.case()["independence"]
        self.assertEqual(3, i["distinct_facsimiles"])
        self.assertEqual(0, i["independent_instrumental_observations_added"])
        self.assertIsNone(i["number_of_underlying_distinct_sensors"])

    def test_change_october_period_rejected(self):
        d = copy.deepcopy(self.parents)
        d["C241-L68"]["row"]["nodal_period_minutes"] = "94.7"
        with self.assertRaises(ValueError):
            bridge.build(d)

    def test_change_october_cutoff_rejected(self):
        d = copy.deepcopy(self.parents)
        d["C241-L68"]["source"]["report_as_of_utc"] = "1963-10-15T00:00:00Z"
        with self.assertRaises(ValueError):
            bridge.build(d)

    def test_change_omega_launch_date_rejected(self):
        d = copy.deepcopy(self.parents)
        d["C241-L67"]["contemporary_rows"][0]["launch"] = "17 JUN"
        with self.assertRaises(ValueError):
            bridge.build(d)

    def test_change_omega_retrospective_catalog_rejected(self):
        d = copy.deepcopy(self.parents)
        d["C241-L67"]["retrospective_rows"][0]["catalog_number"] = 309
        with self.assertRaises(ValueError):
            bridge.build(d)

    def test_change_ancestor_row_rejected(self):
        d = copy.deepcopy(self.parents)
        d["C241-L66"]["sources"]["contemporary_1963"]["visually_read_rows"][0]["launch"] = "17 JUN"
        with self.assertRaises(ValueError):
            bridge.build(d)

    def test_change_existing_bridge_activation_rejected(self):
        d = copy.deepcopy(self.parents)
        d["ABELHA-L64-R59"]["activation"] = True
        with self.assertRaises(ValueError):
            bridge.build(d)

    def test_reject_fake_instrumental_epoch(self):
        p = self.case()
        p["october_catalogue"]["instrumental_observation_epoch_utc"] = "1963-10-15T12:00:00Z"
        with self.assertRaises(ValueError):
            bridge.validate(p)

    def test_reject_fake_sensor_independence(self):
        p = self.case()
        p["independence"]["number_of_underlying_distinct_sensors"] = 3
        with self.assertRaises(ValueError):
            bridge.validate(p)

    def test_reject_lifted_parameter(self):
        p = self.case()
        p["simulator_parameters"][0]["value"] = 100.0
        with self.assertRaises(ValueError):
            bridge.validate(p)

    def test_reject_duplicate_graph_edge(self):
        p = self.case()
        p["graph"].append(copy.deepcopy(p["graph"][0]))
        with self.assertRaises(ValueError):
            bridge.validate(p)

    def test_reject_mutated_input_bytes_even_valid_json(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for path, _ in bridge.INPUTS.values():
                p = root / path
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes((ROOT / path).read_bytes())
            changed = root / bridge.INPUTS["C241-L68"][0]
            changed.write_bytes(changed.read_bytes() + b" ")
            with self.assertRaisesRegex(ValueError, "input SHA drift"):
                bridge.load(root)


if __name__ == "__main__":
    unittest.main()
