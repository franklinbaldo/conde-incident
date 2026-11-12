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

if __name__=="__main__":unittest.main()
