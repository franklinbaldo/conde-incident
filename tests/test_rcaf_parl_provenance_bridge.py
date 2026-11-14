"""Adversarial epistemic audit: network contributions cannot become a NORAD 528 measurement."""
import copy
import json
import pathlib
import shutil
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools import export_rcaf_parl_provenance_bridge as bridge

class RcafParlBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources, cls.hashes = bridge.load()

    def mutate(self, ident, fn):
        sources = copy.deepcopy(self.sources)
        fn(sources[ident])
        with self.assertRaises(ValueError):
            bridge.build(sources, self.hashes)

    def test_byte_exact_and_inactive_graph(self):
        exported = json.loads(bridge.render())
        self.assertEqual(bridge.render(), bridge.OUT.read_bytes())
        self.assertEqual(exported["id"], "ABELHA-C241-L55-L56-01")
        self.assertEqual(len(exported["document_anchors"]), 6)
        self.assertEqual(len(exported["graph"]), 23)
        self.assertEqual({x["id"] for x in exported["stations"]},
                         {"SITE:COLD_LAKE_OPTICAL_CAMERA", "SITE:PRINCE_ALBERT_RADAR"})
        self.assertEqual(exported["named_527_528_529_observations_recovered"], 0)
        self.assertIsNone(exported["independent_instrumental_families_established_for_528"])
        self.assertFalse(exported["physical_constraint_active"])
        self.assertEqual(exported["physical_domain_effect"], "THETA_UNCHANGED")
        self.assertTrue(all(not x["activation"] and x["value"] is None for x in exported["latents"]))
        self.assertTrue(all(not x["activation"] and x["value"] is None
                            for x in exported["simulator_parameters"]))
        self.assertTrue(all(not x["active"] and not x["instrumental_528_measurement"]
                            for x in exported["graph"]))
        self.assertEqual(exported["existing_parent"]["pdf_sha256"],
                         exported["sources"][1]["pdf_sha256"])

    def test_manifest_git_blob_pinned_and_duplicate_keys_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            for rel, _ in bridge.SOURCES.values():
                path = root / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(ROOT / rel, path)
            self.assertEqual(bridge.render(root), bridge.render())
            path = root / bridge.SOURCES["C241-L56"][0]
            path.write_bytes(path.read_bytes() + b" ")
            with self.assertRaisesRegex(ValueError, "source blob drift"):
                bridge.render(root)
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            json.loads('{"named_528":null,"named_528":"528"}',
                       object_pairs_hook=bridge.unique_keys)

    def test_rcaf_network_is_not_528_measurement(self):
        self.mutate("C241-L55", lambda x: x.update(norad_528_observation_utc="1963-11-08T01:00Z"))
        self.mutate("C241-L55", lambda x: x.update(cold_lake_named_observations_recovered=1))
        self.mutate("C241-L55", lambda x: x["independence"].update(independent_instrumental_observations_recovered=1))
        self.mutate("C241-L55", lambda x: x.update(physical_constraint_active=True))
        self.mutate("C241-L55", lambda x: x["source"].update(printed_page=6))
        self.mutate("C241-L55", lambda x: x["anchors"][0].update(text="a NORAD 528 observation"))

    def test_norad_cannot_turn_parl_feed_into_528_return(self):
        self.mutate("C241-L56", lambda x: x["scope"].update(named_528=528))
        self.mutate("C241-L56", lambda x: x["scope"].update(utc_528="1963-11-08T04:00Z"))
        self.mutate("C241-L56", lambda x: x["scope"].update(data_receipt_528=True))
        self.mutate("C241-L56", lambda x: x["scope"].update(independent_sensors_528=2))
        self.mutate("C241-L56", lambda x: x["scope"].update(physical_constraint_active=True))
        self.mutate("C241-L56", lambda x: x["anchors"][1].update(printed_page=55))

    def test_norad_parent_is_same_binary(self):
        self.mutate("C241-L56", lambda x: x.update(parent_id="C241-L55"))
        self.mutate("C241-L56", lambda x: x.update(source_independence="INDEPENDENT_SENSOR"))
        self.mutate("C241-L56", lambda x: x.update(source_sha256=bridge.RCAF_PDF_SHA))
        self.mutate("C241-L56", lambda x: x.update(parent_sha256="0" * 64))

    def test_source_does_not_equate_two_stations_or_dates(self):
        self.mutate("C241-L55", lambda x: x["anchors"][1].update(id="RCAF_COLD_LAKE_SPADATS"))
        self.mutate("C241-L56", lambda x: x["anchors"][2].update(pdf_page_zero_based=70))
        self.mutate("C241-L56", lambda x: x["anchors"][2].update(phrase="observed 528 on 8 November"))
        self.mutate("C241-L55", lambda x: x["source"].update(publication_date_precision="DAY"))
        
if __name__ == "__main__":
    unittest.main()
