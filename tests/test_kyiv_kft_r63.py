"""Fail-closed adversarial tests for instrument chronology and archival citations."""
import copy
import json
import unittest
from tools.audit_kyiv_kft_r63 import MANIFEST, validate

class TestKyivKftR63(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_reference_passes(self):
        self.assertTrue(validate(self.original))

    def test_false_1963_kft_and_delays_rejected(self):
        for key, value in [
            ("instrument_received_from_moscow_year", 1963),
            ("observatory_prepared_instrument_year", 1963),
            ("additional_chronograph_shutter_timing_project_year", 1963),
            ("timing_delays_report_year", 1963),
            ("timing_delays_s", {"chronograph": 0.002, "shutter": 0.001}),
        ]:
            with self.subTest(key=key):
                altered = copy.deepcopy(self.original)
                altered["historical_facts"][key] = value
                with self.assertRaises(ValueError):
                    validate(altered)

    def test_unsupported_evidence_promotion_rejected(self):
        mutations = [
            ("kft_1023_in_service_in_1963", True),
            ("may_transfer_1976_precision_to_1963", True),
            ("original_archival_files_read", True),
            ("observations_identified_norad_527_528_529", [{"norad": 528}]),
            ("new_orbital_constraints", 1),
            ("archive_contacted", True),
        ]
        for key, value in mutations:
            with self.subTest(key=key):
                altered = copy.deepcopy(self.original)
                altered["boundaries"][key] = value
                with self.assertRaises(ValueError):
                    validate(altered)

    def test_not_reclassify_web_visualization_as_pdf_download(self):
        for key, value in [
            ("pdf_bytes_recovered_in_executor", True),
            ("pdf_bytes_sha256", "a" * 64),
            ("pdf_bytes_length", 1),
            ("printed_page_visual_checked", 264),
            ("doi", "invalid"),
        ]:
            with self.subTest(key=key):
                altered = copy.deepcopy(self.original)
                altered["source"][key] = value
                with self.assertRaises(ValueError):
                    validate(altered)

    def test_original_archival_shelfmarks_unchanged(self):
        for key, value in [("file", "ССШСЗ-04-18-99"), ("leaves", "0-100"), ("source_page", 260)]:
            with self.subTest(key=key):
                altered = copy.deepcopy(self.original)
                altered["archival_followups"][0][key] = value
                with self.assertRaises(ValueError):
                    validate(altered)

if __name__ == "__main__":
    unittest.main()
