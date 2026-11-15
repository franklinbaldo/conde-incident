"""Adversarial tests: the Iguape newspaper story cannot become Conde evidence."""

import copy
import json
import unittest

from tools.audit_correio_manha_tartaruga_r74 import MANIFEST, validate


class TestR74(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.good = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_canonical(self):
        self.assertTrue(validate(self.good))

    def mutate(self, path, value):
        doc = copy.deepcopy(self.good)
        parent = doc
        for key in path[:-1]:
            parent = parent[key]
        parent[path[-1]] = value
        with self.assertRaises(ValueError):
            validate(doc)

    def test_time_invented(self):
        self.mutate(["article", "conde_event_time_literal"], "20h30")

    def test_witness_conflated(self):
        self.mutate(["article", "conde_eyewitness"], "Ruth de Souza")

    def test_new_event_link(self):
        self.mutate(["article", "conde_event_link_claimed"], True)

    def test_sp_locality_replaced(self):
        self.mutate(["article", "reported_location"], "CONDE_BA")

    def test_full_edition_false_negative(self):
        self.mutate(["source", "full_edition_read"], True)

    def test_page5_false_full_read(self):
        self.mutate(["source", "full_page_5_read"], True)

    def test_reading_scope_emptied(self):
        self.mutate(["scope", "remaining_pdf_pages_not_fully_reviewed"], [])

    def test_date_event_confusion(self):
        self.mutate(["article", "day_inference_is_not_a_verbatim_date"], False)

    def test_sha_changed(self):
        self.mutate(["source", "sha256"], "0" * 64)

    def test_extra_claim(self):
        doc = copy.deepcopy(self.good)
        doc["article"]["new_norad_identification"] = "528"
        with self.assertRaises(ValueError):
            validate(doc)


if __name__ == "__main__":
    unittest.main()
