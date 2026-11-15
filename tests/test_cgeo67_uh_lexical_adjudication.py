"""Adversarial guards for CGEO-67 passage-level review."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import cgeo67_uh_lexical_adjudication_validate as v


class TestCGEO67(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads(v.FILE.read_text(encoding="utf-8"))
        cls.inv = json.loads(v.INVENTORY.read_text(encoding="utf-8"))
        cls.cover = json.loads(v.COVERS.read_text(encoding="utf-8"))
        cls.prereg = json.loads(v.PREREG.read_text(encoding="utf-8"))

    def test_original(self):
        self.assertEqual(v.validate(self.doc, self.inv, self.cover, self.prereg), 3)

    def rejects(self, mutation):
        altered = copy.deepcopy(self.doc)
        mutation(altered)
        with self.assertRaises((ValueError, KeyError)):
            v.validate(altered, self.inv, self.cover, self.prereg)

    def test_date_not_relabelled(self):
        self.rejects(lambda d: d["adjudicated_passages"][1].update(date="1963-11-08"))

    def test_pinned_pdf_sha(self):
        self.rejects(lambda d: d["adjudicated_passages"][0].update(source_sha256="0" * 64))

    def test_page_not_moved(self):
        self.rejects(lambda d: d["adjudicated_passages"][1].update(pdf_page=8))

    def test_different_article_not_conde(self):
        self.rejects(lambda d: d["adjudicated_passages"][2].update(independent_conde_witness=True))

    def test_football_esfera_not_metal_sphere(self):
        self.rejects(lambda d: d["adjudicated_passages"][0].update(lexical_fragment_match=True))

    def test_fabric_measurement_not_crater(self):
        self.rejects(lambda d: d["adjudicated_passages"][1].update(lexical_fragment_match=True))

    def test_same_day_match_not_erased(self):
        self.rejects(lambda d: d["adjudicated_passages"][2].update(lexical_fragment_match=False))

    def test_context_not_silently_rewritten(self):
        self.rejects(lambda d: d["adjudicated_passages"][2].update(context="Conde eyewitness at 19:30"))

    def test_not_whole_page(self):
        self.rejects(lambda d: d["adjudicated_passages"][0].update(whole_page_read=True))

    def test_no_fake_denominator(self):
        self.rejects(lambda d: d["coverage"].update(pages_fully_read_for_rates=3))

    def test_no_zero_rate(self):
        self.rejects(lambda d: d["coverage"].update(baseline_rates={"F03":0}))

    def test_no_lexical_verdict(self):
        self.rejects(lambda d: d["interpretation"].update(verdict="SUPPORTS_NULL"))

    def test_same_day_is_not_pre_event(self):
        self.rejects(lambda d: d["interpretation"].update(same_day_publication_is_pre_event=True))

    def test_no_fraud_assertion(self):
        self.rejects(lambda d: d["interpretation"].update(narrative_fabrication_proven=True))

    def test_unresolved_ocr_cannot_be_adjudicated(self):
        self.rejects(lambda d: d["unresolved_ocr_leads"][0].update(status="NEGATIVE_SEARCH_RESULT"))

    def test_prereg_unchanged(self):
        self.rejects(lambda d: d.update(prereg_blob_sha="0" * 40))

    def test_no_duplicate_passage(self):
        self.rejects(lambda d: d["adjudicated_passages"].append(copy.deepcopy(d["adjudicated_passages"][0])))


if __name__ == "__main__":
    unittest.main()
