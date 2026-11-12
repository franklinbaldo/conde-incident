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

    def test_renamed_raw_cell_cannot_bypass_facsimile_erratum(self):
        bad = copy.deepcopy(self.raw)
        old = "SSR-1963-11-30-NORAD527-nodal_period"
        forged = old + "-alternate"
        next(o for o in bad["observations"] if o["id"] == old)["id"] = forged
        next(d for d in bad["derived_connections"] if d["id"] ==
             "SSR-PUBLICATIONS-DELTA-527-nodal_period")["inputs"][1] = forged
        with self.assertRaisesRegex(ValueError, "NASA facsimile row identity mismatch"):
            validate(bad)

    def test_handoff_missing_erratum_row_is_rejected(self):
        from texugo_ssr_facsimile_erratum import reconcile_handoff, ROW_ID
        valid = validate(self.raw)
        forged = copy.deepcopy(valid)
        forged["observations"] = [r for r in forged["observations"]
                                  if r["observation"] != ROW_ID]
        with self.assertRaisesRegex(ValueError, "NASA facsimile handoff row set mismatch"):
            reconcile_handoff(self.raw, forged)

    def test_handoff_duplicate_or_missing_delta_is_rejected(self):
        from texugo_ssr_facsimile_erratum import reconcile_handoff, DELTA_ID
        valid = validate(self.raw)
        for variant in ("missing", "duplicate"):
            with self.subTest(variant=variant):
                forged = copy.deepcopy(valid)
                if variant == "missing":
                    forged["derived_connections"] = [e for e in forged["derived_connections"]
                                                      if e["id"] != DELTA_ID]
                else:
                    forged["derived_connections"].append(
                        next(e for e in forged["derived_connections"] if e["id"] == DELTA_ID))
                with self.assertRaisesRegex(ValueError, "NASA facsimile handoff delta"):
                    reconcile_handoff(self.raw, forged)

if __name__ == "__main__":
    unittest.main()
