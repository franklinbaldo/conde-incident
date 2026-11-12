"""Controles de proveniência para documentos originais NORAD 1961–1964.

Prova somente consistência do grafo transcrito de fontes visualmente conferidas,
não autentica bytes remotos nem converte um radar alheio em observação do 528.
"""
import json
from datetime import datetime, timezone
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "research/constraints/morcego_norad_1963_radar_source_audit.json"


class MorcegoNoradSourceAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(SOURCE.read_text(encoding="utf-8"))
        cls.sources = {s["id"]: s for s in cls.data["sources"]}
        cls.occ = {o["id"]: o for o in cls.data["occurrences"]}
        cls.variables = {v["id"]: v for v in cls.data["variables"]}

    def test_five_original_occurrences_are_traceable(self):
        self.assertEqual(len(self.sources), 5)
        self.assertEqual(len(self.occ), 5)
        self.assertEqual(len(self.variables), 11)
        for occurrence in self.occ.values():
            self.assertIn(occurrence["source_id"], self.sources)
            self.assertFalse(occurrence["physical_constraint_active"])
            src = self.sources[occurrence["source_id"]]
            self.assertEqual(src["original_document_verified"], "SCREENSHOT_AND_TEXT")
            self.assertIsNone(src["original_pdf_sha256"])
            self.assertTrue(src["url"].startswith("https://"))

    def test_catalog_1963_mistake_fails_original_1964_year_check(self):
        for id in ("MOR-NORAD-1964-NOV30-09", "MOR-NORAD-1964-NOV30-10"):
            src = self.sources[id]
            self.assertEqual(src["catalog_date_claim"], "1963-11-30")
            self.assertEqual(src["document_date"], "1964-11-30")
            self.assertIn("1964", src["grade"])
        self.assertEqual(self.variables["report09_original_year"]["value"], 1964)
        self.assertEqual(self.variables["report10_original_year"]["value"], 1964)

    def test_1963_decay_window_is_not_528(self):
        src = self.sources["MOR-NORAD-1963-NOV14"]
        self.assertEqual(src["document_date"], "1963-11-14")
        lower = datetime.fromisoformat(self.variables["spadats688_decay_lower_utc"]["value"].replace("Z", "+00:00"))
        upper = datetime.fromisoformat(self.variables["spadats688_decay_upper_utc"]["value"].replace("Z", "+00:00"))
        self.assertEqual(lower.tzinfo, timezone.utc)
        self.assertEqual((upper-lower).total_seconds(), 110*60)
        self.assertEqual(lower.date().isoformat(), "1963-11-12")
        self.assertEqual(upper.date().isoformat(), "1963-11-13")
        self.assertIsNone(self.variables["norad528_true_terminal_utc"]["value"])
        self.assertIsNone(self.variables["nov1963_528_detailed_radar_window_exists"]["value"])
        self.assertFalse(self.data["november_1963_528_observation_found"])

    def test_no_comparison_constraints_leak_to_528(self):
        self.assertEqual(len(self.data["edges"]), 4)
        known = set(self.variables)
        for edge in self.data["edges"]:
            self.assertTrue(set(edge["depends_on"]).issubset(known))
            self.assertFalse(edge["physical_528_constraint_active"])
        self.assertEqual(self.data["domain_528"], "UNALTERED_NOT_EVALUABLE_FROM_COMPARISON_DOCUMENTS")

    def test_norad_nasa_lineage_not_independent_samples(self):
        self.assertEqual(self.sources["MOR-NORAD-1963-NOV12"]["lineage"],
                         self.sources["MOR-NORAD-1963-NOV14"]["lineage"])
        self.assertEqual(self.sources["MOR-NORAD-1964-NOV30-09"]["lineage"],
                         self.sources["MOR-NORAD-1964-NOV30-10"]["lineage"])
        provenance = next(e for e in self.data["edges"] if e["id"] == "1961_BIDIRECTIONAL_NASA_NORAD_LINEAGE")
        self.assertEqual(provenance["level"], "PROVENANCE_ACTIVE")

    def test_contemporaneous_radar_times_do_not_become_528_measurements(self):
        det = self.variables["sputnik46_shemya_radar_detection_utc"]
        self.assertEqual(det["value"], "1963-11-11T06:42:00Z")
        self.assertIn("NOT_528", det["status"])
        self.assertEqual(self.variables["spadats688_reported_decay_interval_error"]["value"], None)


if __name__ == "__main__":
    unittest.main()
