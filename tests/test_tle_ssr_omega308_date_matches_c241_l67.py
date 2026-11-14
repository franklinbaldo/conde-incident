"""C241-L67 fail-closed tests: dates, identity, duplicates and lineage."""
import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import tle_ssr_omega308_date_matches_c241_l67 as a


class DateMatchTest(unittest.TestCase):
    def setUp(self):
        self.data = a.load(a.DATA)
        self.parent = a.load(a.PARENT)

    def changed(self, *path, value):
        item = copy.deepcopy(self.data)
        node = item
        for key in path[:-1]:
            node = node[key]
        node[path[-1]] = value
        with self.assertRaises(ValueError):
            a.validate(item, self.parent)

    def test_valid(self):
        self.assertTrue(a.validate(self.data, self.parent))
        self.assertEqual(len(a.derive(self.data["contemporary_rows"],
                                      self.data["retrospective_rows"])), 3)

    def test_third_row_is_a_alpha_5_not_omega_4(self):
        self.changed("retrospective_rows", 2, "printed_name", value="OMEGA 4")

    def test_third_row_catalog_314(self):
        self.changed("retrospective_rows", 2, "catalog_number", value=308)

    def test_third_row_decay(self):
        self.changed("retrospective_rows", 2, "decay", value="15 JUL 62")

    def test_first_row_label_shift(self):
        self.changed("date_signature_matches", 0, "retrospective_name", value="OMEGA 1")

    def test_second_row_label_shift(self):
        self.changed("date_signature_matches", 1, "retrospective_name", value="OMEGA 2")

    def test_no_1963_norad(self):
        self.changed("editions", "contemporary", "catalog_number_printed", value=True)

    def test_no_calibration(self):
        self.changed("limits", "terminal_sigma_seconds", value=60)

    def test_no_geo_update(self):
        self.changed("limits", "active_constraint_528", value=True)

    def test_no_new_instrument(self):
        self.changed("limits", "independent_instrumental_measurements", value=1)

    def test_historical_mcmc_not_run(self):
        self.changed("limits", "historical_mcmc", value="PASS")

    def test_ambiguous_signature_rejected_by_matcher(self):
        rows = copy.deepcopy(self.data["retrospective_rows"])
        rows[2]["decay"] = rows[1]["decay"]
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            a.derive(self.data["contemporary_rows"], rows)

    def test_no_missing_signature(self):
        rows = copy.deepcopy(self.data["retrospective_rows"])
        rows[2]["decay"] = "15 JUL 62"
        with self.assertRaisesRegex(ValueError, "unmatched"):
            a.derive(self.data["contemporary_rows"], rows)

    def test_parent_hash_tamper(self):
        p = copy.deepcopy(self.parent)
        p["sources"]["retrospective_1977"]["sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            a.validate(self.data, p)

    def test_reject_json_duplicate_keys(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            a.no_duplicate_keys([("id", "A"), ("id", "B")])


if __name__ == "__main__":
    unittest.main()
