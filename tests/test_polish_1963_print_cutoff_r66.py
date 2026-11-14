"""Adversarial checks for original printing versus November 1963 observation."""
import copy
import json
import unittest

from tools.audit_polish_1963_print_cutoff_r66 import MANIFEST, validate


class TestPolish1963PrintCutoff(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_original(self):
        self.assertTrue(validate(self.source))

    def test_checksum_and_print_dates_pinned(self):
        for key, value in [
            ("pdf_sha256", "0" * 64), ("pdf_bytes", 5014392),
            ("colophon_pdf_page_one_based", 3),
            ("editorial_print_handoff_date", "1963-11-12"),
            ("printing_completed_month", "1963-11"),
        ]:
            with self.subTest(key=key):
                d = copy.deepcopy(self.source)
                d["source"][key] = value
                with self.assertRaises(ValueError):
                    validate(d)

    def test_cannot_expand_negative_to_station_network(self):
        for key in ("all_other_polish_journals_excluded", "all_station_logs_excluded", "later_errata_checked"):
            with self.subTest(key=key):
                d = copy.deepcopy(self.source)
                d["limits"][key] = True
                with self.assertRaises(ValueError):
                    validate(d)

    def test_no_fabricated_object_observations(self):
        for key, value in [
            ("norad_527_528_529_rows", [{"norad": 528, "observed_utc": "1963-11-07T12:00:00Z"}]),
            ("independent_observations_recovered", 1),
            ("new_orbital_constraints", 1),
            ("original_1963_satellite_station_log_recovered", True),
        ]:
            with self.subTest(key=key):
                d = copy.deepcopy(self.source)
                d["limits"][key] = value
                with self.assertRaises(ValueError):
                    validate(d)

    def test_report_date_must_not_be_pulled_into_october(self):
        d = copy.deepcopy(self.source)
        d["chronology"]["investigated_report_date"] = "1963-10-07"
        with self.assertRaises(ValueError):
            validate(d)


if __name__ == "__main__":
    unittest.main()
