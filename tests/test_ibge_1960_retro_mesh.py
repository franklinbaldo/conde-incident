"""Evidence-based offline audit of IBGE 1960 retrospective Conde polygon record."""
from __future__ import annotations
import base64,copy,importlib.util,json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts/archives/audit_ibge_1960_conde.py"
SPEC=importlib.util.spec_from_file_location("audit_ibge_1960",SCRIPT)
assert SPEC is not None and SPEC.loader is not None
audit=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)
FIXTURE=ROOT/"tests/fixtures/ibge_conde_1960_shp_record.b64"
MANIFEST=ROOT/"research/geo/ibge_conde_1960_retro_mesh_2026-11-12.json"


class IbgeRetro1960Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record=base64.b64decode(FIXTURE.read_text().strip(),validate=True)
        cls.manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_real_source_polygon_sha_and_topology(self):
        self.assertEqual(audit.digest(self.record),audit.SHAPE_SHA)
        geometry=audit.parse_record(self.record)
        self.assertEqual(geometry["record_sha256"],audit.SHAPE_SHA)
        self.assertEqual(geometry["record_bytes"],808)
        self.assertEqual(geometry["shapefile_record_1based"],2449)
        self.assertEqual(geometry["vertex_count_including_closure"],47)
        self.assertEqual(geometry["projected_bbox_m"],[1761251.25,-1390060.375,1795968.5,-1336775.625])
        self.assertTrue(geometry["ring_closed"])

    def test_1960_reconstruction_not_1963_survey(self):
        audit.validate_manifest(self.manifest,self.record)
        limits=self.manifest["method_and_limits"]
        self.assertFalse(limits["admissible_historical_boundary_1963"])
        self.assertFalse(limits["orbital_constraint_activated"])
        self.assertIsNone(limits["horizontal_accuracy_m"])
        self.assertIsNone(limits["source_legal_boundary_1963"])
        self.assertEqual(limits["geographic_status"],"RETROSPECTIVE_COARSE_PROXY_ONLY")

    def test_official_zip_digest_inventory(self):
        source=self.manifest["source"]
        self.assertEqual(source["url"],audit.URL)
        self.assertEqual(source["binary"]["source_zip_sha256"],audit.ZIP_SHA)
        self.assertEqual(source["binary"]["source_zip_bytes"],2222445)
        self.assertEqual(len(source["binary"]["source_components"]),7)
        self.assertEqual(source["binary"]["dbf_total_records"],2766)
        self.assertEqual(source["binary"]["municipality_code"],"2908606")

    def test_corruption_of_real_source_record_fails(self):
        for offset in (0,12,len(self.record)-1):
            changed=bytearray(self.record)
            changed[offset]^=1
            with self.subTest(offset=offset),self.assertRaisesRegex(ValueError,"hash mismatch"):
                audit.parse_record(bytes(changed))

    def test_unjustified_boundary_claims_rejected(self):
        for key,value in (
            ("admissible_historical_boundary_1963",True),
            ("orbital_constraint_activated",True),
            ("source_legal_boundary_1963",[[1,2]]),
            ("horizontal_accuracy_m",0),
            ("verified_intervening_legal_changes_1960_1963",True),
            ("geographic_status","CONFIRMED_1963")
        ):
            report=copy.deepcopy(self.manifest)
            report["method_and_limits"][key]=value
            with self.subTest(field=key),self.assertRaisesRegex(ValueError,"unjustified"):
                audit.validate_manifest(report,self.record)

    def test_artifact_modification_detected(self):
        report=copy.deepcopy(self.manifest)
        report["source"]["binary"]["projected_bbox_m"][0]+=1
        with self.assertRaisesRegex(ValueError,"source geometry mismatch"):
            audit.validate_manifest(report,self.record)

    def test_temporal_epistemology(self):
        report=self.manifest
        self.assertEqual(report["source"]["archive_year_label"],1960)
        self.assertEqual(report["source"]["publication_year"],2011)
        self.assertIn("2013",report["scope"])
        self.assertIn("SIRGAS_2000",report["source"]["binary"]["crs_wkt"])

if __name__=="__main__":
    unittest.main()
