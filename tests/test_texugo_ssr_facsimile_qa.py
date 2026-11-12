"""Source-table falsification of NASA SSR 1963 3A and 3C (not orbit fit)."""
import copy
import json
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "formal/scripts"))
from check_cumulative_connections import validate

class FacsimileQATests(unittest.TestCase):
    def setUp(self):
        self.raw = json.loads((ROOT / "research/constraints/ssr_1963_observable_graph.json").read_text())

    def test_original_blob_preserved_but_handoff_corrected(self):
        original = next(x for x in self.raw["observations"] if x["id"] == "SSR-1963-11-30-NORAD527-nodal_period")
        self.assertEqual(original["value"], 94.8)
        out = validate(self.raw)
        row = next(x for x in out["observations"] if x["observation"] == original["id"])
        delta = next(x for x in out["derived_connections"] if x["id"] == "SSR-PUBLICATIONS-DELTA-527-nodal_period")
        self.assertEqual(row["reported_value"], 94.6)
        self.assertEqual(row["canonical_value"], 5676.0)
        self.assertEqual(delta["derived_arithmetic"], 0.0)
        self.assertEqual(original["value"], 94.8)
        self.assertEqual(out["facsimile_audit"]["directly_inspected_rows"], 16)
        self.assertEqual(out["constraints_activated"], 0)

    def test_plausible_nasa_forgery_even_with_matched_arithmetic_fails(self):
        bad = copy.deepcopy(self.raw)
        next(x for x in bad["observations"] if x["id"] == "SSR-1963-11-30-NORAD529-apogee")["value"] = 392
        next(x for x in bad["derived_connections"] if x["id"] == "SSR-PUBLICATIONS-DELTA-529-apogee")["derived_arithmetic"] = -28
        with self.assertRaisesRegex(ValueError, "NASA facsimile source-value mismatch"):
            validate(bad)

    def test_silent_legacy_rewrite_is_not_an_erratum(self):
        bad = copy.deepcopy(self.raw)
        next(x for x in bad["observations"] if x["id"] == "SSR-1963-11-30-NORAD527-nodal_period")["value"] = 94.6
        next(x for x in bad["derived_connections"] if x["id"] == "SSR-PUBLICATIONS-DELTA-527-nodal_period")["derived_arithmetic"] = 0.0
        with self.assertRaisesRegex(ValueError, "NASA facsimile source-value mismatch"):
            validate(bad)

if __name__ == "__main__":
    unittest.main()
