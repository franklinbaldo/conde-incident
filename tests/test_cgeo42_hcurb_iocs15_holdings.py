"""Controles CGEO-42: um quadro bibliográfico não equivale ao mapa."""
import copy
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from tools.cgeo42_hcurb_iocs15_holdings import (
    load_contract, validate_contract, verify_pdf,
)


class CGEO42Tests(unittest.TestCase):
    def setUp(self):
        self.c = load_contract()

    def mutate(self, section, key, value):
        changed = copy.deepcopy(self.c)
        changed[section][key] = value
        with self.assertRaises(ValueError):
            validate_contract(changed)

    def test_actual_documentary_contract(self):
        self.assertEqual(validate_contract(self.c), "CGEO42_HCURB_HOLDINGS_CONTRACT_PASS")

    def test_false_claim_of_original_acquisition(self):
        self.mutate("new_holdings_route", "primary_map_acquired", True)
        self.mutate("new_holdings_route", "individual_copy_digitized", True)

    def test_false_identification_of_physical_copy(self):
        self.mutate("new_holdings_route", "individual_copy_identified", True)

    def test_wrong_map_number_and_scale(self):
        self.mutate("new_holdings_route", "publication_number", 14)
        self.mutate("new_holdings_route", "scale_denominator", 250000)

    def test_no_fake_1963_geometry(self):
        for name, value in (("urban_center_1963", [-37.6, -11.8]),
                            ("georeferenced_polygon", [[-37.6, -11.8]]),
                            ("reentry_location", [-37.6, -11.8]),
                            ("spatial_uncertainty_m", 100)):
            with self.subTest(name=name):
                self.mutate("limits", name, value)
        self.mutate("limits", "can_constrain_orbital_reentry", True)

    def test_no_false_independence_or_edition(self):
        self.mutate("lineage", "hcurb_is_an_independent_survey", True)
        self.mutate("lineage", "comparison_identifies_distinct_editions", True)

    def test_no_hash_substitution(self):
        self.mutate("reference_document", "pdf_sha256", "0" * 64)
        self.mutate("reference_document", "pdf_bytes", 0)

    def test_no_silent_change_of_document_page(self):
        self.mutate("reference_document", "table_pdf_page_1based", 8)

    def test_no_imaginary_catalogue_match(self):
        changed = copy.deepcopy(self.c)
        changed["comparison"][0]["physical_identity_resolved"] = True
        with self.assertRaises(ValueError):
            validate_contract(changed)

    def test_fake_binary_not_full_replay(self):
        with TemporaryDirectory() as tmp:
            f = Path(tmp) / "paper.pdf"
            f.write_bytes(b"%PDF-1.5\n%%EOF\n")
            with self.assertRaises(ValueError):
                verify_pdf(f, self.c)


if __name__ == "__main__":
    unittest.main()
