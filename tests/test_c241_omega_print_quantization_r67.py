"""R67 adversarial synthetic fixtures; historical replay is a separate CI step."""
from __future__ import annotations

import copy
from datetime import datetime, timedelta
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from c241_omega1_308_crosssource_r65 import compare
from c241_omega_print_quantization_r67 import audit

ROOT = Path(__file__).resolve().parents[1]
SSR = json.loads((ROOT / "research/tle_custody/nasa_ssr_omega1_oct15_C241-L68.json").read_text())
LAST = datetime.fromisoformat("1963-10-14T23:23:55.702464+00:00")
CUTOFF = datetime.fromisoformat("1963-10-15T12:00:00+00:00")


def fixture():
    # Synthetic epoch list only, not historical orbital claims.
    def row(epoch):
        return {"norad_id": 308, "epoch": epoch, "mean_motion": 16.06513231,
                "eccentricity": 0.0007948999991640449,
                "inclination": 82.14600372314453,
                "intl_designator": "62024  A"}
    epochs = [LAST - timedelta(hours=i) for i in range(44)]
    epochs.extend(CUTOFF + timedelta(hours=i) for i in range(8))
    return compare(SSR, [row(t) for t in epochs])


class QuantizationTests(unittest.TestCase):
    def test_conditional_mismatches_not_identity(self):
        x = audit(fixture())
        self.assertEqual(set(x["mismatches_under_hypothesis"]),
                         {"period_minutes", "apogee_km", "perigee_km"})
        self.assertTrue(x["comparisons"]["inclination_degrees"]["inside_conditional_cell"])
        self.assertEqual(x["comparisons"]["period_minutes"]["conditional_rounding_cell_lower"], "89.65")
        self.assertEqual(x["comparisons"]["period_minutes"]["conditional_rounding_cell_upper_exclusive"], "89.75")
        self.assertEqual(x["comparisons"]["period_minutes"]["minimum_conditional_bridge_magnitude"], "0.014883886")
        self.assertEqual(x["comparisons"]["apogee_km"]["minimum_conditional_bridge_magnitude"], "0.800474139")
        self.assertEqual(x["comparisons"]["perigee_km"]["minimum_conditional_bridge_magnitude"], "2.348101927")
        i = x["scientific_interpretation"]
        self.assertFalse(i["orbit_identity_rejected"])
        self.assertFalse(i["orbit_identity_established"])
        self.assertIsNone(i["terminal_sigma_hours"])
        self.assertEqual(i["historical_mcmc"], "NOT_RUN")
        self.assertFalse(i["active_constraint_528"])

    def test_exact_boundaries_half_up(self):
        r = fixture()
        r["candidate"]["period_minutes_from_mean_motion"] = 89.65
        x = audit(r)
        self.assertTrue(x["comparisons"]["period_minutes"]["inside_conditional_cell"])
        r["candidate"]["period_minutes_from_mean_motion"] = 89.75
        self.assertFalse(audit(r)["comparisons"]["period_minutes"]["inside_conditional_cell"])

    def test_nonfinite_rejected(self):
        for bad in (float("nan"), float("inf"), float("-inf"), True, None, "x"):
            with self.subTest(bad=bad):
                r = fixture()
                r["candidate"]["kepler_perigee_proxy_km"] = bad
                with self.assertRaises(ValueError):
                    audit(r)

    def test_editing_primary_hash_rejected(self):
        r = fixture()
        r["sources"]["primary_ssr_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "provenance"):
            audit(r)

    def test_independence_cannot_be_promoted(self):
        r = fixture()
        r["sources"]["lineage_independence_established"] = True
        with self.assertRaisesRegex(ValueError, "lineage"):
            audit(r)

    def test_cannot_forge_printed_norad(self):
        r = fixture()
        r["printed_row"]["norad_id_printed"] = 308
        with self.assertRaisesRegex(ValueError, "preconditions"):
            audit(r)

    def test_cannot_replace_editorial_cutoff_with_instrumental_epoch(self):
        r = fixture()
        r["printed_row"]["report_as_of_utc_NOT_OBSERVATION"] = "1963-10-14T23:23:55Z"
        with self.assertRaisesRegex(ValueError, "preconditions"):
            audit(r)

    def test_cannot_claim_period_equality(self):
        r = fixture()
        r["comparison_caveats"]["nodal_period_equals_tle_kepler_period"] = True
        with self.assertRaisesRegex(ValueError, "preconditions"):
            audit(r)

    def test_cannot_promote_mcmc(self):
        r = fixture()
        r["inference"]["historical_mcmc"] = "RUN"
        with self.assertRaisesRegex(ValueError, "preconditions"):
            audit(r)

    def test_cannot_forge_printed_precision(self):
        r = fixture()
        r["printed_row"]["nodal_period_minutes"] = 89.6
        with self.assertRaisesRegex(ValueError, "printed"):
            audit(r)

    def test_wrong_schema(self):
        r = fixture()
        r["schema"] = "other"
        with self.assertRaisesRegex(ValueError, "schema"):
            audit(r)

    def test_candidate_count_holds_only_to_real_replay(self):
        r = fixture()
        r["candidate"]["pre_cutoff_epochs"] = 45
        with self.assertRaisesRegex(ValueError, "preconditions"):
            audit(r)


if __name__ == "__main__":
    unittest.main()
