"""R65 regression and hostile mutation tests; stdlib only."""
import copy
from datetime import datetime, timezone, timedelta
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from c241_omega1_308_crosssource_r65 import CUTOFF, compare, verify_ssr

SSR = json.loads((Path(__file__).resolve().parents[1] /
                  "research/tle_custody/nasa_ssr_omega1_oct15_C241-L68.json").read_text())
BASE_EPOCH = datetime.fromisoformat("1963-10-14T23:23:55.702464+00:00")


def row(epoch=BASE_EPOCH, n=16.06513231, inc=82.14600372314453):
    return {"norad_id": 308, "epoch": epoch, "mean_motion": n,
            "eccentricity": 0.0007948999991640449, "inclination": inc,
            "intl_designator": "62024  A"}


class EvidenceTests(unittest.TestCase):
    def test_real_source_rows_pinned(self):
        verify_ssr(SSR)

    def test_evidence_not_probability(self):
        x = compare(SSR, [row()])
        self.assertFalse(x["sources"]["lineage_independence_established"])
        self.assertIsNone(x["printed_row"]["norad_id_printed"])
        self.assertIsNone(x["inference"]["identity_probability"])
        self.assertIsNone(x["inference"]["terminal_sigma_hours"])
        self.assertFalse(x["inference"]["active_constraint_528"])
        self.assertEqual(x["inference"]["historical_mcmc"], "NOT_RUN")

    def test_latest_prior_invariant_post_cutoff_leakage(self):
        x = compare(SSR, [row(), row(epoch=CUTOFF, n=19),
                          row(epoch=CUTOFF + timedelta(days=1), n=20)])
        self.assertEqual(x["candidate"]["pre_cutoff_epochs"], 1)
        self.assertEqual(x["candidate"]["excluded_at_or_after_cutoff"], 2)
        self.assertAlmostEqual(x["candidate"]["period_minutes_from_mean_motion"], 1440/16.06513231)

    def test_identical_duplicate_is_not_new_epoch(self):
        x = compare(SSR, [row(), row()])
        self.assertEqual(x["candidate"]["unique_epochs"], 1)

    def test_conflicting_duplicate_rejected(self):
        with self.assertRaisesRegex(ValueError, "conflicting"):
            compare(SSR, [row(), row(n=15)])

    def test_no_prior_rejected(self):
        with self.assertRaisesRegex(ValueError, "no pre-cutoff"):
            compare(SSR, [row(epoch=CUTOFF)])

    def test_wrong_object_rejected(self):
        r = row()
        r["norad_id"] = 307
        with self.assertRaisesRegex(ValueError, "NORAD"):
            compare(SSR, [r])

    def test_wrong_designator_rejected(self):
        r = row()
        r["intl_designator"] = "62024  B"
        with self.assertRaisesRegex(ValueError, "designator"):
            compare(SSR, [r])

    def test_timezone_naive_rejected(self):
        with self.assertRaisesRegex(ValueError, "UTC"):
            compare(SSR, [row(epoch=BASE_EPOCH.replace(tzinfo=None))])

    def test_invalid_number_rejected(self):
        for val in (float("nan"), float("inf"), 0, -1, True):
            with self.subTest(val=val), self.assertRaises(ValueError):
                compare(SSR, [row(n=val)])

    def test_report_cutoff_cannot_become_observation(self):
        s = copy.deepcopy(SSR)
        s["limits"]["as_of_is_instrumental_epoch"] = True
        with self.assertRaisesRegex(ValueError, "promoted"):
            compare(s, [row()])

    def test_cannot_insert_norad_id_in_ssr_row(self):
        s = copy.deepcopy(SSR)
        s["row"]["catalog_number_printed"] = 308
        with self.assertRaisesRegex(ValueError, "printed"):
            compare(s, [row()])

    def test_cannot_promote_independent_instrument(self):
        s = copy.deepcopy(SSR)
        s["limits"]["independent_instrumental_observations_added"] = 1
        with self.assertRaisesRegex(ValueError, "promoted"):
            compare(s, [row()])

    def test_reject_modified_as_of(self):
        s = copy.deepcopy(SSR)
        s["source"]["report_as_of_utc"] = "1963-10-14T23:23:55Z"
        with self.assertRaisesRegex(ValueError, "as-of"):
            compare(s, [row()])

    def test_quantitative_contrast_is_not_strict_rounding_match(self):
        x = compare(SSR, [row()])
        d = x["difference_candidate_minus_printed"]
        self.assertAlmostEqual(d["period_minutes"], -0.0648838856, places=6)
        self.assertAlmostEqual(d["inclination_degrees"], -0.0039962769, places=6)
        self.assertAlmostEqual(d["apogee_proxy_km"], -1.300474139, places=5)
        self.assertAlmostEqual(d["perigee_proxy_km"], -2.848101927, places=5)
        self.assertFalse(x["comparison_caveats"]["numerical_fingerprint_proves_identity"])

if __name__ == "__main__":
    unittest.main()
