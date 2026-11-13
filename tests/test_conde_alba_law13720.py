"""Adversarial checks for the official 2017 ALBA law, never a 1963 map."""
import copy
import hashlib
import json
import os
from pathlib import Path
import unittest

from tools.verify_conde_alba_law13720 import validate, verify_bytes

DOC = json.loads((Path(__file__).resolve().parents[1] /
                  "research/archive/conde_alba_law13720_custody_20261113.json")
                 .read_text(encoding="utf-8"))


class CondeLaw2017Tests(unittest.TestCase):
    def test_pinned_manifest(self):
        self.assertEqual(validate(DOC), [])

    def test_four_edges_are_closed_2017_only(self):
        self.assertEqual(len(DOC["boundary_cycle_2017"]), 4)
        self.assertEqual(len(DOC["reciprocal_references_2017"]), 3)

    def test_wrong_order_and_broken_cycle_fail(self):
        bad = copy.deepcopy(DOC)
        bad["boundary_cycle_2017"][2]["from"] = "salobrinho"
        self.assertTrue(validate(bad))
        bad = copy.deepcopy(DOC)
        bad["boundary_cycle_2017"].reverse()
        self.assertTrue(validate(bad))

    def test_reverse_attestations_fail_if_swapped(self):
        bad = copy.deepcopy(DOC)
        bad["reciprocal_references_2017"][0]["from"] = "salobrinho"
        self.assertTrue(validate(bad))
        bad = copy.deepcopy(DOC)
        bad["reciprocal_references_2017"][1]["section"] = "8-III"
        self.assertTrue(validate(bad))

    def test_coordinates_cannot_be_silently_modified(self):
        bad = copy.deepcopy(DOC)
        bad["boundary_anchors_2017"][0]["lat_dms"] = "-11°39'45,90\""
        self.assertTrue(validate(bad))

    def test_publication_and_source_identity(self):
        for change in (("publication_date", "1963-11-08"),
                       ("publication_issue", "9"), ("original_url", "https://example.invalid")):
            bad = copy.deepcopy(DOC)
            bad[change[0]] = change[1]
            self.assertTrue(validate(bad))

    def test_no_retroprojection_or_fictional_wayback(self):
        for key in ("1963_legal_boundary_demonstrated",
                    "independent_1963_boundary_survey",
                    "orbital_constraint_activated",
                    "law_2017_coordinates_are_1963_observations"):
            bad = copy.deepcopy(DOC)
            bad["epistemology"][key] = True
            self.assertTrue(validate(bad), key)
        bad = copy.deepcopy(DOC)
        bad["custody"]["archive_url"] = "https://web.archive.org/web/fake"
        self.assertTrue(validate(bad))

    def test_1953_annexes_and_intervening_acts_are_not_read(self):
        for key in ("recovered_1953_facsimile", "recovered_1953_annexes",
                    "checked_intervening_acts_1954_1963"):
            bad = copy.deepcopy(DOC)
            bad["legal_genealogy"][key] = True
            self.assertTrue(validate(bad), key)

    def test_pdf_mutation_and_page_tree(self):
        # Deliberately synthetic tiny bytes: rejection paths, not a historical document.
        fixture = b"%PDF-1.6\n/Type /Page\n%%EOF\n"
        metadata = {"custody": {
            "bytes": len(fixture), "sha256": hashlib.sha256(fixture).hexdigest(),
            "pdf_leaf_page_count": 1}}
        self.assertEqual(verify_bytes(fixture, metadata), [])
        self.assertTrue(verify_bytes(fixture.replace(b"Page", b"Rage"), metadata))
        self.assertTrue(verify_bytes(fixture.replace(b"Page", b"Pade"), metadata))
        self.assertTrue(verify_bytes(fixture[:-6], metadata))
        self.assertTrue(verify_bytes(b"not-pdf", metadata))

    def test_real_official_pdf_if_provided(self):
        path = os.environ.get("CONDE_ALBA_2017_PDF")
        if path and Path(path).is_file():
            self.assertEqual(verify_bytes(Path(path).read_bytes(), DOC), [])
        else:
            self.skipTest("original PDF not bundled with Git checkout")


if __name__ == "__main__":
    unittest.main()
