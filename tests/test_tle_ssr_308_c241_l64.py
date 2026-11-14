"""C241-L64: tests run normally and under Python -O, not using assert for guards."""
import copy
from pathlib import Path
import sys
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import tle_ssr_308_c241_l64 as audit


class C241L64Test(unittest.TestCase):
    def setUp(self):
        self.record = audit.load()

    def reject(self, *path_and_value):
        *path, value = path_and_value
        data = copy.deepcopy(self.record)
        obj = data
        for key in path[:-1]:
            obj = obj[key]
        obj[path[-1]] = value
        with self.assertRaises(ValueError):
            audit.validate(data)

    def test_positive(self):
        self.assertTrue(audit.validate(self.record))

    def test_no_midnight(self):
        self.reject("original_row", "terminal_utc", "1963-10-30T00:00:00Z")

    def test_no_utc_interval(self):
        self.reject("original_row", "utc_interval", ["1963-10-29T00:00Z", "1963-10-31T00:00Z"])

    def test_no_sigma(self):
        self.reject("original_row", "sigma_seconds", 86400)

    def test_no_sensor(self):
        self.reject("original_row", "sensor", "SPADATS RADAR")

    def test_no_station(self):
        self.reject("original_row", "station", "Cold Lake")

    def test_norad_not_printed(self):
        self.reject("original_row", "printed_norad_id", 308)

    def test_range_not_reduced_to_one_day(self):
        self.reject("original_row", "decay_printed", "30 OCT 63")

    def test_launch_day_not_shifted(self):
        self.reject("original_row", "launch_printed", "17 JUN")

    def test_crosswalk_secondary(self):
        self.reject("identity", "identity_status", "PRIMARY_NORAD_CONFIRMED")

    def test_edition21_not_known_absent(self):
        self.reject("archive_search", "no21_nonexistence_established", True)

    def test_no_528_activation(self):
        self.reject("inference", "hard_constraints_528_added", 1)

    def test_no_independent_sensor(self):
        self.reject("inference", "independent_original_sensor_observations_added", 1)

    def test_no_confident_timing(self):
        self.reject("inference", "calibrated_terminal_utc_added", 1)

    def test_hash_tamper(self):
        self.reject("source", "pdf_sha256", "0" * 64)

    def test_duplicate_keys(self):
        with self.assertRaises(ValueError):
            audit.no_duplicate_keys([("duplicate", 1), ("duplicate", 2)])

    def test_wrong_pdf(self):
        with self.assertRaises(ValueError):
            audit.verify_pdf(ROOT / "AGENTS.md")


if __name__ == "__main__":
    unittest.main()
