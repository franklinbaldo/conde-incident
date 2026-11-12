"""A-628 archival processing chronology: no false event dates, receipt claims or physical constraints."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "research/constraints/morcego_a628_processing_dates_20261112.json"


class AirgramChronologyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(PATH.read_text(encoding="utf-8"))
        cls.records = {r["id"]: r for r in cls.data["records"]}

    def test_source_has_only_one_independence_family(self):
        s = self.data["source"]
        self.assertEqual(s["source_family"], "US_DEPARTMENT_OF_STATE_A628")
        self.assertIn("not a new independent witness", s["independence"])
        self.assertIsNone(s["sha256"])
        self.assertFalse(s["original_clippings_in_public_pdf"])

    def test_explicit_dating_marks_and_typo_are_not_interchangeable(self):
        dates = {r["kind"]: [] for r in self.records.values()}
        for r in self.records.values():
            dates[r["kind"]].append(r["date_iso"])
        self.assertEqual(dates["DOCUMENT_DATE_TYPED"], ["1963-11-20"])
        self.assertEqual(dates["ADMINISTRATIVE_DATE_STAMP"], ["1963-11-24", "1963-11-26"])
        self.assertEqual(dates["CONFLICTING_SUBJECT_EVENT_YEAR"], ["1964-11-08"])

    def test_stamps_dont_assert_receipt_or_space_tracking(self):
        for r in self.records.values():
            self.assertFalse(r["physical_observation"])
            if r["kind"] == "ADMINISTRATIVE_DATE_STAMP":
                self.assertIn("UNKNOWN_OFFICE_AND_EVENT", r["date_semantics"])
        for item in self.data["typed_variables"]:
            if item["name"] in {"top_stamp_function", "bottom_stamp_function", "document_transit_dates"}:
                self.assertIsNone(item["value"])
        self.assertFalse(self.data["interpretation"]["candidate_lean_restriction"]["activates_physical_orbital_constraints"])

    def test_all_documentary_edges_are_traceable(self):
        ids = set(self.records) | {"C09#1"}
        for link in self.data["links"]:
            self.assertIn(link["from"], ids)
            self.assertIn(link["to"], ids)
            self.assertNotEqual(link["status"], "ACTIVE_PHYSICAL_CONSTRAINT")

    def test_seven_typed_variables_and_no_fabricated_domain_shrink(self):
        self.assertEqual(len(self.data["typed_variables"]), 7)
        self.assertEqual(self.data["interpretation"]["physical_feasible_domain_status"], "UNCHANGED_NOT_EVALUATED")


if __name__ == "__main__":
    unittest.main()
