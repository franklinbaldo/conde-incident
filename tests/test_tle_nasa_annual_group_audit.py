"""Adversarial structural controls; not independent historic observations."""
import copy
import json
from pathlib import Path
import unittest

from tools.tle_nasa_annual_group_audit import audit

BASE = Path(__file__).resolve().parents[1] / "research" / "tle_custody"


def load(path):
    return json.loads((BASE / path).read_text(encoding="utf-8"))


class AnnualGroupTests(unittest.TestCase):
    def setUp(self):
        self.annual = load("nasa_sp4004_1963_group_custody_C241-L15.json")
        self.october = load("nasa_ssr_1963_oct15_C241-L12.json")
        self.november = load("nasa_ssr_1963_incremental_lineage_C241-L11.json")

    def result(self, doc=None, octdoc=None, novdoc=None, pdf=None):
        return audit(doc if doc is not None else self.annual,
                     octdoc if octdoc is not None else self.october,
                     novdoc if novdoc is not None else self.november, pdf)

    def mutate(self, section, key, new):
        doc = copy.deepcopy(self.annual)
        doc[section][key] = new
        with self.assertRaises(ValueError):
            self.result(doc)

    def test_positive_custody_without_pdf(self):
        report = self.result()
        self.assertEqual(report["pdf_integrity"], "NOT_RUN")
        self.assertIsNone(report["specific_upstream"])
        self.assertFalse(report["annual_status_assignable_to_528"])

    def test_bad_bytes(self):
        with self.assertRaises(ValueError):
            self.result(pdf=b"synthetic PDF is not a historical source")

    def test_promoted_aggregate_status(self):
        self.mutate("inference_guard", "aggregate_status_is_528_status", True)

    def test_synthetic_tle_epoch(self):
        self.mutate("annual_row_extracted_text", "observation_epoch", "1963-12-31")

    def test_wrong_designator(self):
        self.mutate("annual_row_extracted_text", "international_designation_printed", "1963-3B")

    def test_wrong_unit_value(self):
        self.mutate("annual_row_extracted_text", "perigee_statute_miles_printed", 460)

    def test_unsupported_independence(self):
        self.mutate("methodological_note", "measurement_independence", "INDEPENDENT")

    def test_fake_visual_verification(self):
        self.mutate("publication", "page_image_verified", True)

    def test_wrong_linked_day(self):
        self.mutate("linked_sources", "november_decay_day", "1963-11-09")

    def test_wrong_ssr_lineage(self):
        octdoc = copy.deepcopy(self.october)
        octdoc["catalog_rows"][1]["printed"] = "1963 3D"
        with self.assertRaises(ValueError):
            self.result(octdoc=octdoc)

    def test_invented_identity(self):
        self.mutate("inference_guard", "physical_identity_528", "Agena B")

    def test_zero_sigma(self):
        self.mutate("inference_guard", "instrument_sigma", 0)

    def test_promoted_lean_constraint(self):
        self.mutate("inference_guard", "lean_constraint", "PROVEN")


if __name__ == "__main__":
    unittest.main()
