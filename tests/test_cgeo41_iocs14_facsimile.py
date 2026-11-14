"""Testes adversariais: publicação 14 não é publicação 15."""
import copy
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from tools.cgeo41_iocs14_facsimile import load_contract, validate_contract, verify_pdf


class CGEO41Tests(unittest.TestCase):
    def setUp(self):
        self.contract = load_contract()

    def reject(self, section, key, changed):
        copy_contract = copy.deepcopy(self.contract)
        copy_contract[section][key] = changed
        with self.assertRaises(ValueError):
            validate_contract(copy_contract)

    def test_actual_contract(self):
        self.assertEqual(validate_contract(self.contract), "CGEO41_DOCUMENT_CUSTODY_CONTRACT_PASS")

    def test_reject_publication_fusion(self):
        for key, value in (("publication_number", 15), ("original_accession", "BR AN,RIO F4.0.MAP.448")):
            with self.subTest(key=key):
                self.reject("source", key, value)

    def test_reject_fake_original_sha(self):
        for key, value in (("pdf_sha256", "0" * 64), ("pdf_sha1", "0" * 40), ("pdf_bytes", 42), ("pdf_acquired", False)):
            with self.subTest(key=key):
                self.reject("source", key, value)

    def test_nominal_epoch_not_digitization(self):
        self.reject("source", "nominal_date", "2018-07")
        self.reject("source", "wikimedia_upload_date", "1912-03-01")

    def test_no_imaginary_cartographic_read(self):
        self.reject("source", "visual_cartographic_inspection_completed", True)
        self.reject("source", "selected_conde_footprint_verified", True)

    def test_no_false_genealogy(self):
        for key in ("direct_cartographic_reuse_proven", "independent_observations_proven"):
            self.reject("lineage", key, True)
        changed = copy.deepcopy(self.contract)
        changed["lineage"]["iocs15"]["facsimile_acquired"] = True
        with self.assertRaises(ValueError):
            validate_contract(changed)

    def test_no_orbital_position(self):
        for key, val in (("conde_present_on_map", True),
                         ("coverage_of_conde", [1, 2, 3]),
                         ("center_1963", [-37.6, -11.8]),
                         ("reported_fall_location", [-37.6, -11.8]),
                         ("reported_fall_uncertainty_m", 50)):
            with self.subTest(key=key):
                self.reject("limits", key, val)
        self.reject("limits", "can_constrain_orbital_reentry", True)

    def test_fake_binary_not_replay(self):
        with TemporaryDirectory() as tmp:
            f = Path(tmp) / "fake.pdf"
            f.write_bytes(b"%PDF-1.4\n/Type /Page\n%%EOF")
            with self.assertRaises(ValueError):
                verify_pdf(f, self.contract)


if __name__ == "__main__":
    unittest.main()
