"""Adversarial safeguards for December 1953 draft versus January 1954 law."""
import copy
import json
import unittest
from tools.verify_conde_lei628_projeto423 import MANIFEST, validate, verify_original

class TestLegislativeAntecedent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.good = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_control(self):
        self.assertEqual([], validate(self.good))

    def reject(self, field, value):
        x = copy.deepcopy(self.good)
        obj = x
        for key in field[:-1]: obj = obj[key]
        obj[field[-1]] = value
        self.assertNotEqual([], validate(x))

    def test_cannot_invent_annex_or_1963_polygon(self):
        for key in ("annex_vi_original_located", "jandaira_passage_checked_in_original", "municipal_boundary_1963_proven", "orbital_constraint_activated"):
            self.reject(("research_limits", key), True)

    def test_cannot_promote_draft_to_promulgated_law(self):
        self.reject(("related_enacted_law", "draft_is_enacted_law"), True)
        self.reject(("related_enacted_law", "separate_independent_historical_law"), True)
        self.reject(("related_enacted_law", "relationship_status"), "PROVEN_IDENTICAL_LAW")

    def test_chronology_and_folio(self):
        self.reject(("located_entry", "issue_date_printed"), "1953-12-07")
        self.reject(("located_entry", "meeting_date_in_heading"), "1953-12-11")
        self.reject(("located_entry", "pdf_page_1_based"), 318)
        self.reject(("located_entry", "printed_page_number"), 317)

    def test_no_forged_visual_or_ocr(self):
        self.reject(("located_entry", "visual_page_inspected"), False)
        self.reject(("located_entry", "new_ocr_performed"), True)
        self.reject(("located_entry", "full_annex_vi_on_this_page"), True)

    def test_fingerprint_is_fixed(self):
        self.reject(("source", "bytes"), 1)
        self.reject(("source", "sha256"), "0"*64)
        self.reject(("source", "original_physical_master_compared"), True)

    def test_original_replay_rejects_other_file(self):
        self.assertIn("PDF magic", verify_original(MANIFEST, self.good["source"]))
        self.assertIn("PDF length/hash", verify_original(MANIFEST, self.good["source"]))

if __name__ == "__main__": unittest.main()
