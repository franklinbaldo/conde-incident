"""Adversarial classification checks for institution contact and museum records."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("lontra_sfu_route", ROOT / "tools/verify_sfu_station1078_custodian_route.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class SFUStation1078CustodianRoute(unittest.TestCase):
    def setUp(self):
        self.doc = json.loads(module.MANIFEST.read_text(encoding="utf-8"))

    def reject(self, path, value):
        item = copy.deepcopy(self.doc)
        cursor = item
        for key in path[:-1]:
            cursor = cursor[key]
        cursor[path[-1]] = value
        with self.assertRaises(AssertionError):
            module.validate(item)

    def test_valid_manifest(self):
        self.assertTrue(module.validate(self.doc))

    def test_transport_not_authenticated_by_tls(self):
        for idx in (0, 1):
            with self.subTest(source=idx):
                self.reject(["sources",idx,"tls_certificate_validated"],True)

    def test_contact_not_custodian(self):
        self.reject(["evidence_boundary","institution_contact_is_verified_current_custodian"],True)

    def test_museum_custody_not_established(self):
        self.reject(["evidence_boundary","museum_custody_confirmed"],True)
        self.reject(["sources",1,"museum_station1078_journals_listed"],True)

    def test_no_invented_facsimiles_or_contact(self):
        for field in ("detailed_inventory_or_call_number_known", "institutional_outreach_sent", "pages_or_facsimiles_retrieved"):
            with self.subTest(field=field):
                self.reject(["evidence_boundary",field],True)

    def test_no_ornamental_orbital_measurements(self):
        for field in ("independent_target_measurements", "new_numeric_observables", "orbital_constraints_activated"):
            with self.subTest(field=field):
                self.reject(["evidence_boundary",field],1)

    def test_dates_and_objects_immutable(self):
        self.reject(["evidence_boundary","target_norad_ids"],[527])
        self.reject(["evidence_boundary","dates_to_request"],["1963-11-08"])

    def test_source_hashes_are_fixed(self):
        self.reject(["sources",0,"sha256"],"0"*64)
        self.reject(["sources",1,"bytes"],112262)

    def test_replay_exact_html(self):
        path = Path("/workspace/lontra-r34-sources")
        if not path.is_dir():
            self.skipTest("Source bytes are optional outside Jatobá")
        module.validate(self.doc, [(path/"contact.html").read_bytes(), (path/"node_922.html").read_bytes()])
        with self.assertRaises(AssertionError):
            module.validate(self.doc, [b"x"*110177,(path/"node_922.html").read_bytes()])

if __name__ == "__main__":
    unittest.main()
