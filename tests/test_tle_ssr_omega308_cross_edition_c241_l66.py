"""C241-L66: mandatory positive + adversarial tests under normal and -O."""
from __future__ import annotations
import copy
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import tle_ssr_omega308_cross_edition_c241_l66 as a


class CrossEditionTest(unittest.TestCase):
    def setUp(self):
        self.data = a.load()
        self.legacy = a.load(a.L64)
        self.corr = a.load(a.L65)

    def altered(self, path, value):
        data = copy.deepcopy(self.data)
        node = data
        for part in path[:-1]:
            node = node[part]
        node[path[-1]] = value
        with self.assertRaises(ValueError):
            a.validate(data, self.legacy, self.corr)

    def test_positive(self):
        self.assertTrue(a.validate(self.data, self.legacy, self.corr))

    def test_1977_omega2_not_omega1(self):
        self.altered(["sources", "retrospective_1977", "visually_read_rows", 1,
                      "designator"], "OMEGA 1")

    def test_1977_308_not_307(self):
        self.altered(["sources", "retrospective_1977", "visually_read_rows", 1,
                      "catalog_number"], 307)

    def test_1977_omega1_is_307(self):
        self.altered(["sources", "retrospective_1977", "visually_read_rows", 0,
                      "catalog_number"], 308)

    def test_1963_omega1_not_omega2(self):
        self.altered(["sources", "contemporary_1963", "visually_read_rows", 0,
                      "designator"], "OMEGA 2")

    def test_no_contemporaneous_308_printed(self):
        self.altered(["sources", "contemporary_1963", "printed_norad_number"], 308)

    def test_no_assumed_relabeling_cause(self):
        self.altered(["finding", "cause_of_discrepancy"], "1963 editorial typo")

    def test_no_identity_silent_repair(self):
        self.altered(["finding", "contemporary_omega1_identity_to_308"],
                     "PRIMARY_CONFIRMED")

    def test_not_independent_pdf(self):
        self.altered(["inference", "new_primary_pdf_families"], 1)

    def test_no_sensor(self):
        self.altered(["inference", "sensor"], "SPADATS")

    def test_no_utc(self):
        self.altered(["inference", "terminal_event_utc"], "1963-10-30T00:00:00Z")

    def test_no_sigma(self):
        self.altered(["inference", "terminal_sigma_seconds"], 300)

    def test_no_528_constraint(self):
        self.altered(["inference", "active_constraint_528"], True)

    def test_no_historical_mcmc(self):
        self.altered(["inference", "historical_mcmc"], "PASS")

    def test_pdf_page_is_one_based(self):
        self.altered(["sources", "retrospective_1977", "pdf_page_1based"], 45)

    def test_prior_correction_unchanged(self):
        bad = copy.deepcopy(self.corr)
        bad["corrects"]["correct_value"] = "OMEGA 2"
        with self.assertRaises(ValueError):
            a.validate(self.data, self.legacy, bad)

    def test_duplicate_keys(self):
        with self.assertRaises(ValueError):
            a.without_duplicate_keys([("id", 1), ("id", 2)])

    def test_pdf_corruption(self):
        with tempfile.TemporaryDirectory() as path:
            damaged = Path(path) / "corrupt.pdf"
            damaged.write_bytes(b"%PDF- wrong bytes")
            for year in ["1963", "1977"]:
                with self.subTest(year=year), self.assertRaises(ValueError):
                    a.verify_pdf(damaged, year)


if __name__ == "__main__":
    unittest.main()
