"""Mutations of real NTRS metadata projections; no synthetic orbital records."""
import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.tle_ntrs_ssr_index_audit import LEDGER, analyze, index_21, published_1963


class TestIndex(unittest.TestCase):
    def setUp(self):
        self.lock = json.loads(LEDGER.read_text(encoding="utf-8"))
        self.rows = [{
            "id": r["ntrs_id"], "title": r["title_as_indexed"],
            "otherReportNumbers": r["report_numbers_as_indexed"],
            "publications": [{"publicationDate": r["published_on"] + "T00:00:00Z"}],
        } for r in self.lock["known_records"]]

    def test_all_anchors(self):
        r = analyze(self.rows, self.lock)
        self.assertEqual(len(r["known_source_ids"]), 11)
        self.assertEqual(r["issue_21_status"], "NOT_LOCATED_IN_THIS_QUERY")
        self.assertEqual(r["physical_constraints_activated"], 0)

    def test_bad_query(self):
        self.lock["query"]["q"] = "other"
        with self.assertRaises(ValueError):
            analyze(self.rows, self.lock)

    def test_deleted_anchor(self):
        with self.assertRaises(ValueError):
            analyze(self.rows[:-1], self.lock)

    def test_duplicate_anchor(self):
        with self.assertRaises(ValueError):
            analyze(self.rows + [copy.deepcopy(self.rows[0])], self.lock)

    def test_mutated_title(self):
        self.rows[0]["title"] += " changed"
        with self.assertRaises(ValueError):
            analyze(self.rows, self.lock)

    def test_mutated_crosswalk(self):
        self.lock["known_records"][0]["issue_number_from_project"] = 21
        with self.assertRaises(ValueError):
            analyze(self.rows, self.lock)

    def test_literal_typo(self):
        self.assertTrue(any("Saatellite" in row["title"] for row in self.rows))

    def test_issue_21_specificity(self):
        r = copy.deepcopy(self.rows[0])
        r["title"] = "Satellite Situation Report, Vol. 3, No. 21"
        self.assertTrue(index_21(r))
        r["title"] = "NASA-TM-X-51221"
        self.assertFalse(index_21(r))

    def test_future_index_hit_is_pending_facsimile(self):
        r = copy.deepcopy(self.rows[0])
        r["id"] = 19639999999
        r["title"] = "Satellite Situation Report, Vol. 3, No. 21"
        self.rows.append(r)
        result = analyze(self.rows, self.lock)
        self.assertEqual(result["issue_21_candidate_ids"], [19639999999])
        self.assertEqual(result["instrumental_observations"], 0)

    def test_date_not_derived_from_ntrs_prefix(self):
        r = self.rows[-1]
        self.assertEqual(published_1963(r), "1963-12-31")
        r["publications"][0]["publicationDate"] = "1964-01-01T00:00:00Z"
        self.assertIsNone(published_1963(r))


if __name__ == "__main__":
    unittest.main()

