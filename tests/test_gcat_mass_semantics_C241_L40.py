"""Distinguish GCAT's catalog fields from historical closed mass inventory."""
import json
import sys
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.gcat_mass_semantics_C241_L40 import MANIFEST, field, one_row, replay


class TestC241L40(unittest.TestCase):
    def test_catalog_is_not_a_mass_measurement_of_three_debris(self):
        m = json.loads(MANIFEST.read_text())
        self.assertEqual(m["rows"]["S00527"]["total_mass_kg"], 1176)
        self.assertEqual(m["rows"]["S00527"]["mass_kg"], 306)
        self.assertIsNone(m["rows"]["S00528"]["mass_kg"])
        self.assertIsNone(m["rows"]["S00529"]["mass_kg"])
        self.assertIsNone(m["derived_checks"]["three_norad_objects_mass_sum_kg"])
        self.assertFalse(m["conclusion"]["historical_mass_constraint_active"])

    def test_306_plus_870_is_1176_but_306_plus_900_is_1206(self):
        m = json.loads(MANIFEST.read_text())["rows"]
        self.assertEqual(m["S00527"]["mass_kg"] + m["A00324"]["dry_mass_kg"], 1176)
        self.assertEqual(m["S00527"]["mass_kg"] + m["A00324"]["mass_kg"], 1206)

    def test_exact_column_parser(self):
        self.assertEqual(field("a  0123  zz", "a  Mass  Next", "Mass", "Next"), "0123")
        self.assertEqual(one_row(["X  abc", "Y def"], "X"), "X  abc")
        with self.assertRaises(ValueError):
            one_row(["X abc", "X def"], "X")

    def test_manifest_source_hashes_are_complete(self):
        m = json.loads(MANIFEST.read_text())
        self.assertEqual(set(m["files"]), {
            "satcat.html", "auxcat.html", "psatcat.html",
            "Thor.html", "cols.html", "lcols.html"
        })
        for s in m["files"].values():
            self.assertEqual(len(s["sha256"]), 64)
            self.assertGreater(s["bytes"], 10_000)
            self.assertTrue(s["url"].startswith("https://planet4589.org/"))

    def test_mutation_of_hash_does_not_pass_replay(self):
        m = json.loads(MANIFEST.read_text())
        m["files"]["satcat.html"]["sha256"] = "0" * 64
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            path = tmp / "mutant.json"
            path.write_text(json.dumps(m))
            (tmp / "satcat.html").write_text("broken")
            with self.assertRaises(ValueError):
                replay(tmp, path)


if __name__ == "__main__":
    unittest.main()
