"""Test documentary source-to-source overlap without synthetic sensors."""
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from audit_soviet_nasa_crosswalk_r49 import audit, load


class SovietNasaCrosswalkR49(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.case = load()

    def reject(self, mutate):
        data = copy.deepcopy(self.case)
        mutate(data)
        with self.assertRaises(ValueError):
            audit(*data)

    def test_crosswalk(self):
        self.assertEqual(audit(*self.case), "PAIR_MATCH_BUT_PROVENANCE_UNRESOLVED")

    def test_fake_soviet_norad(self):
        self.reject(lambda x: x[0]["sources"]["soviet"].__setitem__("printed_norad", 527))

    def test_swap_nasa_object_c(self):
        self.reject(lambda x: x[0]["sources"]["nasa"].__setitem__("row_designator", "1963-003C"))

    def test_wrong_nasa_issue(self):
        self.reject(lambda x: x[0]["sources"]["nasa"].__setitem__("ntrs_id", "19640005618"))

    def test_false_exact_period_match(self):
        self.reject(lambda x: x[0]["comparison"]["period_min"].__setitem__("nasa", "94.66"))

    def test_false_simple_rounding(self):
        self.reject(lambda x: x[0]["comparison"]["period_min"].__setitem__(
            "nasa_one_decimal_rounding_of_soviet", True))

    def test_false_inclination_identity(self):
        self.reject(lambda x: x[0]["comparison"]["inclination_deg"].__setitem__("nasa", "81.89"))

    def test_wrong_soviet_apogee(self):
        self.reject(lambda x: x[1]["printed_table_row"].__setitem__("apogee_km_printed", 534))

    def test_wrong_nasa_perigee(self):
        self.reject(lambda x: x[2]["sources"][1]["rows"][0].__setitem__("perigee_km", 458))

    def test_fake_soviet_sensor(self):
        self.reject(lambda x: x[0]["interpretation"].__setitem__(
            "independent_soviet_sensor_or_time_utc_proven", True))

    def test_false_direct_copy_claim(self):
        self.reject(lambda x: x[0]["interpretation"].__setitem__(
            "direct_soviet_copy_from_this_nasa_issue_proven", True))

    def test_fake_constraints(self):
        self.reject(lambda x: x[0]["interpretation"].__setitem__(
            "new_physical_constraints_activated", 1))

    def test_fake_new_measurement(self):
        self.reject(lambda x: x[0]["interpretation"].__setitem__(
            "new_per_object_tracking_measurements", 1))

    def test_wrong_publication_year(self):
        self.reject(lambda x: x[0]["sources"]["soviet"].__setitem__("publication_year", 1963))

    def test_wrong_page(self):
        self.reject(lambda x: x[0]["sources"]["nasa"].__setitem__("pdf_page_one_based", 6))


if __name__ == "__main__":
    unittest.main()
