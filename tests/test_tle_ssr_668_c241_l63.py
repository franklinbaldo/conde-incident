"""C241-L63 adversarial tests, executed normally and under python -O."""
import copy
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import tle_ssr_668_c241_l63 as audit


class C241L63Test(unittest.TestCase):
    def setUp(self):
        self.record = audit.load()

    def test_positive(self):
        self.assertTrue(audit.validate(self.record))

    def reject_mutant(self, path, value):
        data = copy.deepcopy(self.record)
        d = data
        for step in path[:-1]:
            d = d[step]
        d[path[-1]] = value
        with self.assertRaises(ValueError):
            audit.validate(data)

    def test_no_utc(self):
        self.reject_mutant(("catalogue_day", "terminal_utc"), "1963-10-12T00:00Z")

    def test_no_fabricated_interval(self):
        self.reject_mutant(("catalogue_day", "terminal_time_interval"), "00-24 UTC")

    def test_no_fake_station(self):
        self.reject_mutant(("catalogue_day", "instrumental_station"), "Cold Lake")

    def test_no_sensor(self):
        self.reject_mutant(("catalogue_day", "sensor"), "RADAR")

    def test_no_sigma_zero(self):
        self.reject_mutant(("catalogue_day", "error_sigma"), 0)

    def test_no_tle(self):
        self.reject_mutant(("catalogue_day", "raw_tle"), "1 00668U ...")

    def test_no_observation_fabrication(self):
        self.reject_mutant(("catalogue_day", "original_observation"), {})

    def test_wrong_date(self):
        self.reject_mutant(("catalogue_day", "decay_printed"), "13 OCT 63")

    def test_wrong_launch(self):
        self.reject_mutant(("catalogue_day", "launch_printed"), "23 SEP")

    def test_norad_not_printed(self):
        self.reject_mutant(("catalogue_day", "printed_norad_id"), 668)

    def test_not_new_source(self):
        self.reject_mutant(("source", "preexisting_same_publication"), None)

    def test_no_independent_sensor(self):
        self.reject_mutant(("source", "independently_observed_sensor"), True)

    def test_no_un_independence(self):
        self.reject_mutant(("lineage", "independence_of_nasa_and_un"), True)

    def test_no_308_inference(self):
        self.reject_mutant(("unresolved_control", "primary_day"), "1963-10-30")

    def test_no_528_activation(self):
        self.reject_mutant(("inference", "historical_528_constraints_added"), 1)

    def test_no_extra_field(self):
        self.reject_mutant(("catalogue_day", "estimated_utc"), "1963-10-12T00:00Z")

    def test_no_hash_drift(self):
        self.reject_mutant(("source", "pdf_sha256"), "0" * 64)

    def test_no_page_shift(self):
        self.reject_mutant(("source", "zero_based_page"), 7)

    def test_no_duplicate_json_keys(self):
        with self.assertRaises(ValueError):
            audit.unique_object([("year", 1963), ("year", 1964)])

    def test_no_forged_pdf(self):
        with self.assertRaises(ValueError):
            audit.verify_pdf(ROOT / "AGENTS.md")


if __name__ == "__main__":
    unittest.main()
