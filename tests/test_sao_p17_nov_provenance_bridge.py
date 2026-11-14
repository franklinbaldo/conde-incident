"""Adversarial source-locked L61/SAO bridge; -O must not suppress verification."""
from __future__ import annotations
import copy
from pathlib import Path
import sys
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import export_sao_p17_nov_provenance_bridge as bridge
from export_sao_clock_methods_bridge import render as prior_render

class SaoP17NovBridge(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = bridge.load()
        cls.parent = prior_render()

    def test_site_replay_exact_bytes(self):
        self.assertEqual(bridge.OUT.read_bytes(), bridge.render())

    def test_one_p17_pdf_not_two_sensors(self):
        d = bridge.build(self.sources, self.parent)
        a,b = d["source_lineage"]
        self.assertEqual(a["original_pdf_sha256"],b["original_pdf_sha256"])
        self.assertEqual([x["occurrence_id"] for x in d["source_lineage"]],["C241-L44","C241-L61"])
        self.assertEqual(0,d["new_independent_instrumental_measurements_528"])
        self.assertIsNone(d["observations_528_elsewhere_count"])

    def test_clock_step_is_not_utc_epoch(self):
        d = bridge.build(self.sources,self.parent)
        self.assertEqual("0.100000",d["clock"]["difference_at_boundary_seconds"])
        self.assertEqual("2.740565438",d["clock"]["a1_minus_wwv_example_seconds"])
        self.assertFalse(d["clock"]["utc_transform_calibrated"])
        self.assertTrue(d["clock"]["example_is_not_a_528_observation"])

    def test_graph_and_parameters_remain_inactive(self):
        d = bridge.build(self.sources,self.parent)
        self.assertEqual(12,len(d["graph"]))
        self.assertTrue(all(x["activation"] is False for x in d["graph"]))
        self.assertTrue(all(x["activation"] is False and x["value"] is None
                            for x in d["latents"]+d["simulator_parameters"]))
        self.assertEqual("CANDIDATE_ONLY_NOT_COMPILED", d["lean_status"])
        self.assertEqual("THETA_UNCHANGED", d["physical_domain_effect"])

    def mutant(self,sid,path,value):
        src=copy.deepcopy(self.sources)
        at=src[sid]
        for key in path[:-1]:
            at=at[key]
        at[path[-1]]=value
        with self.assertRaises(ValueError):
            bridge.build(src,self.parent)

    def test_reject_fake_528_utc(self):
        self.mutant("C241-L61",["model","utc_conversion_proven"],True)

    def test_reject_fake_528_observation(self):
        self.mutant("C241-L61",["input_528_observation"],{"time":"1963-11-08T01:00:00Z"})

    def test_reject_nonzero_sensor(self):
        self.mutant("C241-L61",["independent_528_observations_added"],1)

    def test_reject_shifted_clock_boundary(self):
        self.mutant("C241-L61",["model","branches"],[
            {"start_mjd":"38030.0","end_mjd_exclusive":"38395.0",
             "intercept_seconds":"2.292725"}])

    def test_reject_falsified_l44_identity(self):
        self.mutant("C241-L44",["source","sha256"],"0"*64)

    def test_reject_l44_global_scope_promotion(self):
        self.mutant("C241-L44",["observed_targets_in_this_publication"],["1963-003B"])

    def test_reject_wrong_lineage(self):
        self.mutant("C241-L61",["dependencies"],["C241-L59"])

    def test_reject_parent_bridge_drift(self):
        with self.assertRaisesRegex(ValueError,"parent bridge"):
            bridge.build(self.sources,self.parent+b" ")

    def test_reject_duplicate_json_keys(self):
        with self.assertRaisesRegex(ValueError,"duplicate JSON key"):
            bridge.unique_pairs([("timestamp","x"),("timestamp","y")])

    def test_reject_source_hash_drift(self):
        with tempfile.TemporaryDirectory() as name:
            base=Path(name)
            for _sid,(path,_digest) in bridge.SOURCES.items():
                dest=base/path
                dest.parent.mkdir(parents=True,exist_ok=True)
                dest.write_bytes((ROOT/path).read_bytes())
            source=base/bridge.SOURCES["C241-L61"][0]
            source.write_bytes(source.read_bytes()+b"\n")
            with self.assertRaisesRegex(ValueError,"manifest SHA drift"):
                bridge.load(base)

if __name__=="__main__":
    unittest.main()

