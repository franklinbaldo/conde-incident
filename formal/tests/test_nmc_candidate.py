"""Conde Y20175 source-to-parameter connection, without invented sonic profiles."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"formal/scripts"))
sys.path.insert(0,str(ROOT))
from compile_nmc_candidate import (compile_bridge,MANIFEST,LINEAGES,MATRIX,
                                    JSON_TARGET,LEAN_TARGET)

class NmcBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest=json.loads(MANIFEST.read_text())
        cls.lineages=json.loads(LINEAGES.read_text())
        cls.matrix=MATRIX.read_bytes()

    def test_real_custody_and_generated_products(self):
        generated,lean=compile_bridge(self.manifest,self.lineages,self.matrix)
        self.assertEqual(generated,JSON_TARGET.read_text())
        self.assertEqual(lean,LEAN_TARGET.read_text())
        doc=json.loads(generated)
        self.assertEqual(doc["numeric_observations_generated"],0)
        self.assertEqual(doc["physical_domain"],"UNCHANGED_NO_ACTIVE_CONSTRAINT")
        self.assertEqual(len(doc["candidate_queries"]),9)
        self.assertEqual(len({(r["station_wmo_candidate"],r["day_utc_candidate"])
                              for r in doc["candidate_queries"]}),9)
        self.assertEqual(doc["matrix_context_ref"].split(":")[-1],"C151#1")
        self.assertEqual(doc["archive_bytes"],117264384)

    def test_no_synthetic_station_hits(self):
        for key,value in (("matches",0),("records_parsed",1),("negative_station_claim",True)):
            fake=copy.deepcopy(self.manifest)
            fake["station_day_audit"][key]=value
            with self.subTest(field=key),self.assertRaises(ValueError):
                compile_bridge(fake,self.lineages,self.matrix)

    def test_tampered_binary_digest_and_source(self):
        fake=copy.deepcopy(self.manifest)
        fake["binary"]["sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"custody"):
            compile_bridge(fake,self.lineages,self.matrix)
        bad=copy.deepcopy(self.lineages)
        target=next(x for x in bad["citations"] if x["occurrence"]=="C151#1")
        target["source_id"]="AFSPC_MIRROR_528"
        with self.assertRaises(ValueError):
            compile_bridge(self.manifest,bad,self.matrix)

    def test_wrong_candidate_station_day_rejected(self):
        fake=copy.deepcopy(self.manifest)
        fake["station_day_audit"]["wmo_codes_target"][0]="12345"
        with self.assertRaisesRegex(ValueError,"station/day"):
            compile_bridge(fake,self.lineages,self.matrix)

class NmcOn20HistoricalLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from tools import export_nmc_on20_layout_link as on20
        from compile_nmc_layout_link import assemble, TARGET
        cls.on20 = on20
        cls.assemble = staticmethod(assemble)
        cls.target = TARGET
        cls.manual = json.loads((ROOT / on20.MANUAL).read_text())
        cls.pages = json.loads((ROOT / on20.PAGES).read_text())
        cls.tape = json.loads((ROOT / on20.TAPE).read_text())
        cls.archive = on20.archive.build(ROOT)

    def test_real_1964_facsimile_connected_to_undecoded_1963_tape(self):
        data = self.on20.build_from_data(self.manual, self.pages, self.tape, self.archive)
        self.assertEqual(self.on20.encode(data), (ROOT / self.on20.OUTPUT).read_bytes())
        self.assertEqual(self.assemble(data), self.target.read_text())
        self.assertEqual(data["manual_publication_year"], 1964)
        self.assertEqual(data["wayback_pdf_bytes"], 932414)
        self.assertEqual(data["revision_date_seen"], "1964-11-27")
        self.assertTrue(data["not_an_independent_documentary_source"])
        self.assertEqual(data["wayback_capture_utc"], "2022-01-19T07:53:33Z")
        self.assertEqual(len(data["lineage"]), 3)
        self.assertIsNone(data["validated_1963_layout_reference"])
        self.assertFalse(data["active_physical_constraint"])

    def test_relabel_1964_manual_as_1963_is_rejected(self):
        changed = copy.deepcopy(self.manual)
        changed["published_year"] = 1963
        with self.assertRaisesRegex(ValueError, "historical manual"):
            self.on20.build_from_data(changed, self.pages, self.tape, self.archive)

    def test_wrong_pdf_hash_or_page_identity_is_rejected(self):
        changed = copy.deepcopy(self.pages)
        changed["pdf_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "page inventory"):
            self.on20.build_from_data(self.manual, changed, self.tape, self.archive)

    def test_false_station_decode_and_wind_activation_are_rejected(self):
        changed = copy.deepcopy(self.tape)
        changed["candidate_queries"][0]["query_status"] = "OBSERVED"
        with self.assertRaisesRegex(ValueError, "Y20175 observations"):
            self.on20.build_from_data(self.manual, self.pages, changed, self.archive)
        changed = copy.deepcopy(self.tape)
        changed["physical_domain"] = "NARROWED"
        with self.assertRaisesRegex(ValueError, "Y20175 observations"):
            self.on20.build_from_data(self.manual, self.pages, changed, self.archive)

    def test_archive_graph_cannot_promote_conditional_manual_to_observation(self):
        changed = copy.deepcopy(self.archive)
        target = next(n for n in changed["nodes"] if n["id"] == "NMC_Y20175_PENDING_BRIDGE")
        target["activation"] = True
        with self.assertRaisesRegex(ValueError, "canonical Abelha"):
            self.on20.build_from_data(self.manual, self.pages, self.tape, changed)

    def test_fabricated_1963_layout_provenance_does_not_compile(self):
        data = self.on20.build_from_data(self.manual, self.pages, self.tape, self.archive)
        data["validated_1963_layout_reference"] = "UNSOURCED"
        with self.assertRaisesRegex(ValueError, "conditionality"):
            self.assemble(data)


if __name__=="__main__":unittest.main()
