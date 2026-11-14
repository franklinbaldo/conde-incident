"""Negative mutation tests: refuse fabricated orbital readings from a service tally."""
import copy
import json
import unittest
from tools.audit_polish_observation_service_r65 import MANIFEST, validate


class TestPolishObservationServiceR65(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_original_passes(self):
        self.assertTrue(validate(self.data))

    def test_digest_or_source_pdf_page_mutation(self):
        for key, value in [("full_pdf_sha256", "0"*64),
                           ("full_pdf_bytes", 4882673),
                           ("pdf_pages_one_based", [29,30]),
                           ("printed_pages", [190,192])]:
            with self.subTest(key=key):
                mutated = copy.deepcopy(self.data)
                mutated["source"][key] = value
                with self.assertRaises(ValueError): validate(mutated)

    def test_25000_cannot_be_read_as_1963_only(self):
        mutated = copy.deepcopy(self.data)
        mutated["reported_service"]["count_scope"] = "YEAR_1963_ONLY"
        with self.assertRaises(ValueError): validate(mutated)

    def test_polish_station_numbers_not_norad_catalog(self):
        mutated = copy.deepcopy(self.data)
        mutated["reported_service"]["cospar_station_id_first"] = 527
        with self.assertRaises(ValueError): validate(mutated)

    def test_no_false_observation_or_sigma(self):
        for key, value in [
            ("observations_for_norad_527_528_529", [{"norad": 528, "date": "1963-11-08"}]),
            ("independent_measurement_rows_recovered", 1),
            ("object_specific_time_observed", "1963-11-08T12:00:00Z"),
            ("individual_station_instrument_calibration_recovered", True),
            ("new_orbital_constraints", 1),
        ]:
            with self.subTest(key=key):
                mutated = copy.deepcopy(self.data)
                mutated["boundaries"][key] = value
                with self.assertRaises(ValueError): validate(mutated)

    def test_report_is_not_raw_instrument_record(self):
        mutated = copy.deepcopy(self.data)
        mutated["boundaries"]["original_station_logs_recovered"] = True
        with self.assertRaises(ValueError): validate(mutated)


if __name__ == "__main__":
    unittest.main()
