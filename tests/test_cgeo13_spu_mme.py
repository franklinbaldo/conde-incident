"""CGEO-13: 1985 institutional map catalogues cannot authenticate 1963 geography."""
from __future__ import annotations

import copy
import json
import unittest

from tools.cgeo13_spu_mme import CONTRACT, evaluate, validate_contract


class SpuMme1985Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = validate_contract(json.loads(CONTRACT.read_text(encoding="utf-8")))

    def test_two_identified_archival_occurrences(self):
        rows = self.data["records"]
        self.assertNotEqual(rows[0]["id"], rows[1]["id"])
        self.assertTrue(all(r["catalog_url"].startswith(
            "https://memoria-spu.gestao.gov.br/") for r in rows))

    def test_different_scales_are_not_error_estimates(self):
        self.assertEqual([r["scale_denominator"] for r in self.data["records"]],
                         [100000, 50000])
        self.assertIsNone(self.data["dependency_graph"]["georeferencing_error_m"])

    def test_1985_revisions_postdate_event(self):
        evaluated = evaluate("1963-11-08", self.data)
        self.assertTrue(evaluated["map_revisions_postdate_requested_date"])
        self.assertIn("MMC 70", self.data["records"][0]["extra_base"])

    def test_no_pdf_bytes_or_fabricated_sha(self):
        for row in self.data["records"]:
            self.assertEqual(row["access_status"], "CATALOGUE_READ_PDF_NOT_ACQUIRED")
            self.assertFalse(row["facsimile_inspected"])
            self.assertIsNone(row["pdf_sha256"])

    def test_catalogued_utm_does_not_establish_crs(self):
        for row in self.data["records"]:
            self.assertIn("UTM", row["catalogued_utm_text"])
            self.assertIsNone(row["geodetic_datum"])
            self.assertIsNone(row["verified_crs"])

    def test_never_promote_geography_on_any_requested_date(self):
        for day in ("1963-11-08", "1970-01-01", "1985-09-01", "2026-11-12"):
            with self.subTest(day=day):
                result = evaluate(day, self.data)
                self.assertIsNone(result["legal_boundary_for_requested_date"])
                self.assertIsNone(result["event_point_membership"])
                self.assertFalse(result["can_constrain_orbital_reentry"])

    def test_mutant_records_fail_closed(self):
        changes = (
            (0, "facsimile_inspected", True),
            (1, "geodetic_datum", "SAD69"),
            (0, "pdf_sha256", "NOT_A_REAL_CHECKSUM"),
            (1, "scale_denominator", 100000),
            (0, "geometry", {"type": "Polygon", "coordinates": []}),
            (1, "verified_crs", "EPSG:32724"),
            (0, "original_date", "1963-11-08"),
        )
        for idx, key, value in changes:
            with self.subTest(key=key, idx=idx):
                mutant = copy.deepcopy(self.data)
                mutant["records"][idx][key] = value
                with self.assertRaises(ValueError):
                    validate_contract(mutant)

    def test_mutant_dependency_graph_fails_closed(self):
        changes = (
            ("same_ibge_family_not_independent_surveys", False),
            ("can_constrain_reentry", True),
            ("legal_boundary_1963", {"type": "Polygon", "coordinates": []}),
            ("datum", "SIRGAS2000"),
            ("point_of_reentry", [-37.6, -11.8]),
        )
        for key, value in changes:
            with self.subTest(key=key):
                mutant = copy.deepcopy(self.data)
                mutant["dependency_graph"][key] = value
                with self.assertRaises(ValueError):
                    validate_contract(mutant)

    def test_documentary_dependency_graph_must_be_preserved(self):
        mutant = copy.deepcopy(self.data)
        mutant["dependency_graph"]["links"].pop()
        with self.assertRaisesRegex(ValueError, "dependency graph"):
            validate_contract(mutant)


if __name__ == "__main__":
    unittest.main()
