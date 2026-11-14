"""C241-L65: counterexamples against name collision and invented precision."""
import copy
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import c241_ssr_omega_corrigendum_r63 as audit


class VisualCorrigendumTest(unittest.TestCase):
    def setUp(self):
        self.old = audit.load(audit.L64)
        self.new = audit.load(audit.L65)

    def mutate(self, section, key, replacement):
        changed = copy.deepcopy(self.new)
        changed[section][key] = replacement
        with self.assertRaises(ValueError):
            audit.validate(self.old, changed)

    def test_baseline(self):
        self.assertTrue(audit.validate(self.old, self.new))

    def test_wrong_legacy_value(self):
        self.old["original_row"]["printed_designator"] = "OMEGA 1"
        with self.assertRaises(ValueError):
            audit.validate(self.old, self.new)

    def test_wrong_corrected_value(self):
        changed = copy.deepcopy(self.new)
        changed["corrects"]["correct_value"] = "A OMEGA 1"
        with self.assertRaises(ValueError):
            audit.validate(self.old, changed)

    def test_distinct_soviet_object(self):
        self.mutate("disambiguation", "other_label", "1962 OMEGA 1")

    def test_wrong_country(self):
        self.mutate("disambiguation", "other_country", "US")

    def test_wrong_launch_date(self):
        self.mutate("disambiguation", "other_launch_date", "1962-06-18")

    def test_wrong_pdf_page(self):
        self.mutate("source", "zero_based_page", 15)

    def test_wrong_pdf_hash(self):
        self.mutate("source", "pdf_sha256", "0" * 64)

    def test_wrong_calendar(self):
        self.mutate("source", "decay_printed", "30 OCT 63")

    def test_norad_promotion(self):
        self.mutate("disambiguation", "primary_norad_id_printed", 308)

    def test_crosswalk_promotion(self):
        self.mutate("disambiguation", "crosswalk_norad_308", "PRIMARY")

    def test_invented_sigma(self):
        self.mutate("inference", "terminal_sigma_hours", 12)

    def test_invented_utc(self):
        self.mutate("inference", "actual_terminal_utc", "1963-10-30T12:00:00Z")

    def test_activated_528(self):
        self.mutate("inference", "active_constraint_528", True)

    def test_duplicate_json_key(self):
        with self.assertRaises(ValueError):
            audit.no_duplicates([("x", 1), ("x", 2)])


if __name__ == "__main__":
    unittest.main()
