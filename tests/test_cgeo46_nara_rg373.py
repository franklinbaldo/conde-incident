"""Adversarial validation of an institutional aerial archive candidate."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("cgeo46", ROOT / "tools/cgeo46_nara_rg373.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
SOURCE = json.loads((ROOT / "research/geo/cgeo46_nara_rg373_overlays.json").read_text())
PRIOR = json.loads((ROOT / "research/geo/cgeo45_mi1850_roll58.json").read_text())


class CandidateTests(unittest.TestCase):
    def test_contract_valid(self):
        module.validate(SOURCE, PRIOR)

    def test_candidate_degree_square(self):
        self.assertEqual(module.degree_square(-11.813, -37.6139), "11S037W")

    def test_nara_northern_example(self):
        self.assertEqual(module.degree_square(48.3, 2.2), "48N002E")

    def test_nara_western_example(self):
        self.assertEqual(module.degree_square(56.2, -3.4), "56N003W")

    def test_out_of_range(self):
        for latitude, longitude in ((91, 10), (-91, 0), (0, -181), (0, 181)):
            with self.subTest(latitude=latitude, longitude=longitude), self.assertRaises(ValueError):
                module.degree_square(latitude, longitude)

    def test_nonfinite(self):
        for value in (float("nan"), float("inf"), -float("inf")):
            with self.subTest(value=value), self.assertRaises(ValueError):
                module.degree_square(value, -37)

    def test_reject_wrong_conde(self):
        d = copy.deepcopy(SOURCE)
        d["candidate"]["state"] = "PB"
        with self.assertRaises(AssertionError):
            module.validate(d, PRIOR)

    def test_reject_assumed_overlay(self):
        d = copy.deepcopy(SOURCE)
        d["candidate"]["catalog_result_status"] = "FOUND"
        with self.assertRaises(AssertionError):
            module.validate(d, PRIOR)

    def test_reject_fabricated_film_can(self):
        d = copy.deepcopy(SOURCE)
        d["nara_identifier_resolution"]["can_id"] = "ON000001"
        with self.assertRaises(AssertionError):
            module.validate(d, PRIOR)

    def test_reject_fabricated_sgb_identity(self):
        d = copy.deepcopy(SOURCE)
        d["nara_identifier_resolution"]["sgb_nara_same_flight"] = True
        with self.assertRaises(AssertionError):
            module.validate(d, PRIOR)

    def test_reject_promoted_center(self):
        d = copy.deepcopy(SOURCE)
        d["limitations"]["center_conde_nov_1963"] = [-37.6139, -11.813]
        with self.assertRaises(AssertionError):
            module.validate(d, PRIOR)

    def test_reject_false_orbital_constraint(self):
        d = copy.deepcopy(SOURCE)
        d["limitations"]["can_constrain_orbital_reentry"] = True
        with self.assertRaises(AssertionError):
            module.validate(d, PRIOR)

    def test_reject_changed_sgb_hash(self):
        d = copy.deepcopy(SOURCE)
        d["sgb_provenance"]["image_sha256"] = "0" * 64
        with self.assertRaises(AssertionError):
            module.validate(d, PRIOR)

    def test_reject_inferred_date(self):
        d = copy.deepcopy(SOURCE)
        d["nara_identifier_resolution"]["flight_date"] = "1963-11-08"
        with self.assertRaises(AssertionError):
            module.validate(d, PRIOR)


if __name__ == "__main__":
    unittest.main()

