"""Negative-control tests for article-level narrative analysis CGEO-68."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import cgeo68_uh_article_boundary_validate as v


class CGeo68Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data, cls.inv, cls.covers, cls.prereg, cls.previous = [
            json.loads(path.read_text(encoding="utf-8")) for path in
            (v.DATA, v.INVENTORY, v.COVERS, v.PREREG, v.PREVIOUS)
        ]

    def fail_on_mutation(self, mutate):
        doc = copy.deepcopy(self.data)
        mutate(doc)
        with self.assertRaises((ValueError, KeyError)):
            v.validate(doc, self.inv, self.covers, self.prereg, self.previous)

    def test_original(self):
        self.assertEqual(v.validate(self.data, self.inv, self.covers,
                                    self.prereg, self.previous), 2)

    def test_original_source_hash(self):
        self.fail_on_mutation(lambda d: d["adjudications"][0].update(source_sha256="0"*64))

    def test_original_source_url(self):
        self.fail_on_mutation(lambda d: d["adjudications"][0].update(source_url="https://example.org/"))

    def test_date_swap(self):
        self.fail_on_mutation(lambda d: d["adjudications"][0].update(date="1963-11-08"))

    def test_page_swap(self):
        self.fail_on_mutation(lambda d: d["adjudications"][1].update(pdf_page=7))

    def test_setback_is_not_crater(self):
        self.fail_on_mutation(lambda d: d["adjudications"][0].update(fragment_match=True))

    def test_window_is_not_spacecraft(self):
        self.fail_on_mutation(lambda d: d["adjudications"][1].update(fragment_match=True))

    def test_same_page_is_not_same_article(self):
        self.fail_on_mutation(lambda d: d["same_page_nonindependence"].update(joint_article_with_both_fragments=True))

    def test_renaming_article_invalid(self):
        self.fail_on_mutation(lambda d: d["same_page_nonindependence"].update(article_B="Police report"))

    def test_no_fake_hour(self):
        self.fail_on_mutation(lambda d: d["interpretation"].update(chronology_same_day_known=True))

    def test_no_fake_conde_witness(self):
        self.fail_on_mutation(lambda d: d["adjudications"][1].update(independent_conde_witness=True))

    def test_no_fraud_verdict(self):
        self.fail_on_mutation(lambda d: d["interpretation"].update(narrative_fabrication_proven=True))

    def test_no_physical_geocode(self):
        self.fail_on_mutation(lambda d: d["interpretation"].update(historical_center_1963=[-11.8,-37.6]))

    def test_no_new_orbital_gate(self):
        self.fail_on_mutation(lambda d: d["interpretation"].update(orbital_constraint_activated=True))

    def test_no_whole_page_credit(self):
        self.fail_on_mutation(lambda d: d["adjudications"][0].update(whole_page_read=True))

    def test_denominator_must_be_zero(self):
        self.fail_on_mutation(lambda d: d["coverage"].update(fully_inspected_newspaper_pages_for_rates=2))

    def test_rate_must_be_unknown(self):
        self.fail_on_mutation(lambda d: d["coverage"].update(baseline_rates={"F03":0}))

    def test_no_duplicate(self):
        self.fail_on_mutation(lambda d: d["adjudications"].append(copy.deepcopy(d["adjudications"][0])))

    def test_context_mutation(self):
        self.fail_on_mutation(lambda d: d["adjudications"][0].update(context="Conde at 20:30"))

    def test_frozen_prereg(self):
        self.fail_on_mutation(lambda d: d.update(prereg_blob_sha="0"*40))


if __name__ == "__main__":
    unittest.main()
