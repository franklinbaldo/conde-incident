"""Adversarial audit of RU263/L52 station holdings versus actual orbital observations."""
import copy
import json
import pathlib
import shutil
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools import export_sao_ru263_spadats_bridge as bridge


class TestRu263Spadats(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data, cls.hashes = bridge.load()

    def mutate(self, identifier, change):
        sources = copy.deepcopy(self.data)
        change(sources[identifier])
        with self.assertRaises(ValueError):
            bridge.build(sources, self.hashes)

    def test_replay_byte_exact_and_claims_disjoint(self):
        data = json.loads(bridge.render())
        self.assertEqual(bridge.render(), bridge.OUT.read_bytes())
        self.assertEqual(data["id"], "ABELHA-C241-L53-L52-01")
        self.assertEqual(len(data["anchors"]), 4)
        self.assertEqual(len(data["events"]), 5)
        self.assertEqual({x["norad_id"] for x in data["catalogue_target_candidates"]},
                         {527, 528, 529})
        self.assertEqual(len(data["graph"]), 28)
        self.assertEqual(len(data["latents"]), 8)
        self.assertEqual(data["confirmed_norad_528_observations_from_manifests"], 0)
        self.assertIsNone(data["unknown_observations_in_unopened_archive"])
        self.assertIsNone(data["independent_instrumental_families"])
        self.assertIsNone(data["actual_1963_sao_to_spadats_528_transfer"])
        self.assertFalse(data["activation"])
        self.assertEqual(data["physical_domain_effect"], "THETA_UNCHANGED")
        self.assertTrue(all(not x["activation"] and x["value"] is None
                            for x in data["latents"]))
        self.assertTrue(all(not e["active"] and not e["independent_instrumental_observation"]
                            for e in data["graph"]))
        self.assertEqual(data["lean_status"],
                         "PENDING_PREMISES_NO_COMPILED_EMPIRICAL_PROOF")

    def test_source_bytes_and_location_are_not_interchangeable(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            for rel, _ in bridge.SOURCES.values():
                p = root / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(ROOT / rel, p)
            self.assertEqual(bridge.render(root), bridge.render())
            p = root / bridge.SOURCES["C241-L53"][0]
            p.write_bytes(p.read_bytes() + b"\n")
            with self.assertRaisesRegex(ValueError, "source bytes drift"):
                bridge.render(root)

    def test_ru263_l53_box_page_and_scope_guards(self):
        self.mutate("C241-L53", lambda x: x["anchors"][0].update(box=67))
        self.mutate("C241-L53", lambda x: x["anchors"][0].update(pdf_page_index_zero_based=14))
        self.mutate("C241-L53", lambda x: x.update(individual_observations_recovered_from_this_finding_aid=1))
        self.mutate("C241-L53", lambda x: x.update(cross_collection_independent_observations=2))
        self.mutate("C241-L53", lambda x: x.update(norad_528_utc="1963-11-08T00:00Z"))
        self.mutate("C241-L53", lambda x: x.update(norad_528_data_received_by_spadats="YES"))

    def test_norad_date_is_not_observation_epoch(self):
        self.mutate("C241-L52", lambda x: x["events"][4].update(date="1963-11-08"))
        self.mutate("C241-L52", lambda x: x["events"][0].update(pdf_page_index=71))
        self.mutate("C241-L52", lambda x: x["scope"].update(epoch_528_utc="1963-11-08T23:59Z"))
        self.mutate("C241-L52", lambda x: x["scope"].update(actual_1963_sao_to_spadats_528_transfer=True))
        self.mutate("C241-L52", lambda x: x["scope"].update(physical_constraint_active=True))

    def test_ru478_shares_sao_program_not_independent_sensor(self):
        self.mutate("C241-L45", lambda x: x.update(derived_from_same_sao_program=False))
        self.mutate("C241-L45", lambda x: x.update(individual_observation_utc="1963-11-08"))
        self.mutate("C241-L45", lambda x: x["anchors"][2].update(id="OTHER-BOX"))

    def test_source_custody_does_not_evidence_object_identity(self):
        self.mutate("C241-L53", lambda x: x.update(norad_528_observation={"ra": 0.0}))
        self.mutate("C241-L52", lambda x: x["scope"].update(physical_piece_528="Agena D"))
        self.mutate("C241-L52", lambda x: x["scope"].update(independent_instrumental_family_count=2))

    def test_no_ambiguous_duplicate_json_keys(self):
        with self.assertRaisesRegex(ValueError, "duplicate key"):
            json.loads('{"activation":false,"activation":true}',
                       object_pairs_hook=bridge.unique_keys)


if __name__ == "__main__":
    unittest.main()
