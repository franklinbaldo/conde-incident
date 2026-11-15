"""Guardas de interpretação da matriz contrafactual C241 G84; não simulam órbitas."""
import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DECISION = ROOT / "research/statistics/c241_document_decision_g84.json"
LEDGER = ROOT / "research/statistics/c241_fbis_plane_ledger_g83.json"
ALLOWED = {"COND_528_ONLY", "COND_637_ONLY", "COND_NONE", "UNDECIDED", "NOT_EVALUABLE"}


class DocumentDecisionG84Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(DECISION.read_text(encoding="utf-8"))
        cls.ledger = json.loads(LEDGER.read_text(encoding="utf-8"))

    def test_no_physical_exclusion_or_new_time(self):
        d = self.data
        self.assertEqual(d["schema"], "conde.c241-document-decision/g84")
        for key in ("physical_compatibility_licensed", "orbit_exclusion_licensed",
                    "active_constraint", "posterior", "orbital_phase_evaluated"):
            self.assertIs(d[key], False, key)
        for key in ("historical_event_time_utc", "verified_fbis_clock", "impact_probability"):
            self.assertIsNone(d[key], key)
        self.assertFalse(self.ledger["orbit_exclusion_licensed"])
        self.assertIsNone(self.ledger["historical_event_time_utc"])

    def test_six_document_families_and_scenario_citations(self):
        d = self.data
        self.assertEqual([x["item"] for x in d["documents"]], [1, 2, 3, 4, 5, 6])
        seen = set()
        for doc in d["documents"]:
            self.assertGreaterEqual(len(doc["scenarios"]), 2)
            for case in doc["scenarios"]:
                self.assertNotIn(case["id"], seen)
                seen.add(case["id"])
                self.assertIn(case["conditional_readout"], ALLOWED)
                self.assertTrue(case["model_528"])
                self.assertTrue(case["model_637"])
                for col in ("source_ids_528", "source_ids_637"):
                    self.assertTrue(case[col])
                    self.assertTrue(set(case[col]).issubset(d["source_files"]))
        self.assertEqual(len(seen), 19)

    def test_g83_fbis_discriminant_not_promoted(self):
        rows = self.ledger["rows"]
        hits = [r for r in rows if r["norad"] == 528 and
                r["crossing_utc"].startswith("1963-11-08T23:4")]
        self.assertEqual(len(hits), 2)
        for r in hits:
            self.assertEqual(r["gmt_conditional_order"], "AFTER")
            self.assertEqual(r["rio_local_conditional_order"], "BEFORE")
            self.assertIsNone(r["independent_event_time_871"])
        self.assertEqual(self.ledger["counts"]["637_CONSTANT_A"]["gmt_before"], 6)
        self.assertEqual(self.ledger["counts"]["637_CONSTANT_A"]["rio_before"], 6)

    def test_nasa_day_is_not_exact_reentry_time(self):
        self.assertTrue(self.ledger["nasa_day_cutoff_not_observed_reentry_instant"])
        self.assertEqual(self.ledger["clock_decision"], "UNRESOLVED")
        self.assertIsNone(self.ledger["conditional_broadcast_other"])


if __name__ == "__main__":
    unittest.main()
