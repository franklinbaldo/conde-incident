"""C241-P7: adversarial checks for documented, non-independent NASA rows."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from ssr_oct15_kepler_j2_nodal import evaluate, period_models_min


class NasaOct15NodalProxyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger = json.loads((
            ROOT / "research/tle_custody/nasa_ssr_1963_oct15_C241-L12.json"
        ).read_text(encoding="utf-8"))

    def test_golden_primary_compilation_and_units(self):
        r = evaluate(self.ledger)
        self.assertEqual(r["source_record"], "C241-L12")
        self.assertEqual(r["source_ntrs"], "19640000428")
        self.assertEqual(r["samples_in_one_compiled_source"], 3)
        self.assertEqual(r["fitted_parameters"], 0)
        self.assertEqual(
            [x["international_designator"] for x in r["objects"]],
            ["1963-003A", "1963-003B", "1963-003C"],
        )
        self.assertAlmostEqual(
            r["objects"][1]["kepler_two_body_period_min"], 92.32494313265562,
            places=8,
        )
        self.assertAlmostEqual(
            r["objects"][1]["j2_first_order_nodal_period_min"], 92.4476585664234,
            places=8,
        )
        self.assertEqual(r["physical_orbit_domain_reduction"], "NONE")
        self.assertFalse(r["promoted_lean_constraint"])

    def test_j2_better_for_b_c_worse_for_a(self):
        r = evaluate(self.ledger)
        a, b, c = r["objects"]
        k = "kepler_signed_pred_minus_printed_seconds"
        j = "j2_signed_pred_minus_printed_seconds"
        self.assertGreater(abs(a[j]), abs(a[k]))
        for row in (b, c):
            self.assertLess(abs(row[j]), abs(row[k]))
        self.assertLess(r["j2_mae_seconds"], r["two_body_mae_seconds"])

    def test_zero_j2_recovers_two_body(self):
        kepler, nodal = period_models_min(401, 376, 81.87, j2=0.0)
        self.assertEqual(kepler, nodal)

    def test_inclination_changes_j2_but_not_kepler(self):
        a, b = period_models_min(401, 376, 0)
        c, d = period_models_min(401, 376, 90)
        self.assertEqual(a, c)
        self.assertNotEqual(b, d)

    def test_invalid_or_nonfinite_parameters_fail_closed(self):
        for args in [
            (-1, -1, 80), (100, 101, 80), (400, 350, 181),
            (400, 350, float("nan")),
        ]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                period_models_min(*args)
        for kwargs in [
            {"mu_km3_s2": 0}, {"radius_km": 0}, {"j2": -1}, {"j2": 1},
        ]:
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                period_models_min(400, 350, 80, **kwargs)

    def test_primary_ledger_mutation_fails_provenance_gate(self):
        changed = copy.deepcopy(self.ledger)
        changed["catalog_rows"][1]["nodal_period_min_printed"] = "92.5"
        with self.assertRaises(ValueError):
            evaluate(changed)

    def test_publication_date_does_not_suppose_tracking_epoch(self):
        r = evaluate(self.ledger)
        self.assertIn("tracking epochs", r["missing"])
        self.assertEqual(
            r["source_lineage"], "NASA_1963_COMPILED_PUBLICATION_NOT_RAW_SENSOR",
        )


if __name__ == "__main__":
    unittest.main()
