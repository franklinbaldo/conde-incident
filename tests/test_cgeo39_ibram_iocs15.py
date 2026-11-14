"""Negative controls for museum map provenance and archival independence."""
import copy
import tempfile
import unittest
from pathlib import Path
from tools.cgeo39_ibram_iocs15 import load_contract, validate_contract, verify_finding_aid

class CGEO39Tests(unittest.TestCase):
    def setUp(self):
        self.doc=load_contract()
    def reject(self,change):
        data=copy.deepcopy(self.doc);change(data)
        with self.assertRaises(ValueError):
            validate_contract(data)
    def test_contract(self):
        self.assertEqual(validate_contract(self.doc),"CGEO39_CONTRACT_PASS")
    def test_holdings_count_and_one_duplicate(self):
        self.reject(lambda d:d["archival_collection"].update(maps_listed=12))
        self.reject(lambda d:d["archival_collection"].update(duplicates_declared=0))
        self.reject(lambda d:d["archival_collection"].update(physical_items_declared=11))
    def test_source_integrity(self):
        self.reject(lambda d:d["archival_collection"].update(finding_aid_pdf_sha256="0"*64))
        self.reject(lambda d:d["archival_collection"].update(finding_aid_pdf_bytes=136247))
        self.reject(lambda d:d["archival_collection"].update(page_zero_index=27))
        self.reject(lambda d:d["archival_collection"].update(printed_page=26))
    def test_holdings_are_not_facsimile(self):
        for key in ("original_item_inspected","individual_map_digitization_acquired","item_level_accession_known","rights_for_republication_verified"):
            with self.subTest(key=key):
                self.reject(lambda d,k=key:d["archival_collection"].update({k:True}))
    def test_cross_custody_is_not_independent_survey(self):
        for key in ("cross_custodian_copy_identity_verified","independent_survey_proven","original_1912_image_acquired","pixel_comparison_performed"):
            with self.subTest(key=key):
                self.reject(lambda d,k=key:d["link"].update({k:True}))
        self.reject(lambda d:d["link"].update(relation="INDEPENDENT_SURVEY"))
    def test_not_event_geometry(self):
        self.reject(lambda d:d["limits"].update(center_1963=[-37,-12]))
        self.reject(lambda d:d["limits"].update(reported_fall=[-37,-12]))
        self.reject(lambda d:d["limits"].update(uncertainty_m=100))
        self.reject(lambda d:d["limits"].update(can_constrain_orbital_reentry=True))
        self.reject(lambda d:d["limits"].update(spatial_coverage_confirmed=True))
    def test_catalogued_work_identity(self):
        self.reject(lambda d:d["prior_archive"].update(publication_number=29))
        self.reject(lambda d:d["prior_archive"].update(physical_copy_identity_with_ibram=True))
        self.reject(lambda d:d["archival_collection"].update(includes_literal_title=""))
    def test_wrong_pdf_bytes_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            wrong=Path(directory)/"fake.pdf"
            wrong.write_bytes(b"%PDF-1.4\n%%EOF")
            with self.assertRaises(ValueError):
                verify_finding_aid(wrong)
            wrong.write_bytes(b"<html>not PDF</html>")
            with self.assertRaises(ValueError):
                verify_finding_aid(wrong)
        with self.assertRaises(FileNotFoundError):
            verify_finding_aid(Path("/no/such/arquivo.pdf"))

if __name__=="__main__":
    unittest.main()
