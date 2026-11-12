"""C241-P3: disallow future field assimilation, invalid trajectories or swapped sources."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from cross_object_epoch_support import FIELDS  # noqa: E402
from raan_fitfield_j2_holdout import (  # noqa: E402
    MAX_NUMERICAL_REFINEMENT_DEG, compare_holdout, fit_field_trends,
    integrate_secular_node_deg, slope_fit_only, state_at,
)
from raan_frozen_trend_holdout import iso  # noqa: E402


def make_state(raan=123.0, n=15.3, ecc=0.004, incl=81.9):
    values = {"inclination": incl, "raan": raan, "eccentricity": ecc, "mean_motion": n}
    return tuple(str(values.get(name, 0)) for name in FIELDS)


def make_row(t, n=15.3, raan=123.0, ecc=0.004, incl=81.9, rowid=1):
    return {"epoch": t, "state": make_state(raan=raan, n=n, ecc=ecc, incl=incl),
            "source_rows": [rowid]}


class FitfieldJ2Tests(unittest.TestCase):
    def setUp(self):
        self.epoch = datetime(1963, 1, 1, tzinfo=timezone.utc)
        self.fit = [make_row(self.epoch+timedelta(days=d), n=15.3+d*0.001,
                             ecc=0.004+d*0.00001,
                             incl=81.9-d*0.0001, raan=123-1.1*d, rowid=d)
                    for d in range(3)]
        self.fit_keys = [iso(r["epoch"]) for r in self.fit]

    def test_known_frozen_field_slopes_units(self):
        model = fit_field_trends(self.fit, self.fit_keys)
        self.assertEqual(model["fit_n"], 3)
        self.assertAlmostEqual(model["fields"]["mean_motion"]["slope_per_day"], 0.001, places=10)
        self.assertAlmostEqual(model["fields"]["eccentricity"]["slope_per_day"], 0.00001, places=10)
        self.assertAlmostEqual(model["fields"]["inclination"]["slope_per_day"], -0.0001, places=10)
        self.assertEqual(model["anchor_source_rows"], [2])

    def test_future_rows_are_not_consulted_for_fit(self):
        anchor = fit_field_trends(self.fit, self.fit_keys)
        altered = make_row(self.epoch+timedelta(days=70), n=15.99,
                           raan=3, incl=120, ecc=0.9, rowid=100)
        self.assertEqual(anchor, fit_field_trends(self.fit+[altered], self.fit_keys))

    def test_freeze_zero_slope_matches_constant_j2_formula(self):
        identical = [make_row(self.epoch+timedelta(days=d), rowid=d)
                     for d in range(3)]
        model = fit_field_trends(identical, [iso(r["epoch"]) for r in identical])
        from raan_fitfield_j2_holdout import j2_nodal_deg_day
        h = 35.5
        result = integrate_secular_node_deg(model, h)
        self.assertAlmostEqual(result["nodal_delta_deg"],
                               j2_nodal_deg_day(model["anchor_state"])*h, places=7)
        self.assertLess(result["numerical_refinement_delta_deg"], MAX_NUMERICAL_REFINEMENT_DEG)

    def test_reject_nonphysical_extrapolated_mean_motion(self):
        model = fit_field_trends(self.fit, self.fit_keys)
        model["fields"]["mean_motion"]["slope_per_day"] = -12
        with self.assertRaisesRegex(ValueError, "invalid J2 input"):
            integrate_secular_node_deg(model, 2)

    def test_invalid_fit_manifest_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate FIT membership"):
            fit_field_trends(self.fit, [self.fit_keys[0],self.fit_keys[0],self.fit_keys[1]])
        with self.assertRaises(KeyError):
            fit_field_trends(self.fit, self.fit_keys[:2]+["1963-02-01T00:00:00.000000Z"])
        with self.assertRaisesRegex(ValueError, "ordered or repeated"):
            slope_fit_only([1,1,2],[2,3,4])

    def test_holdout_cannot_launder_changed_epochs_or_raan(self):
        model = fit_field_trends(self.fit, self.fit_keys)
        future = make_row(self.epoch+timedelta(days=10),raan=123, rowid=100)

        baseline = {"n":1, "details":[{"epoch_utc":iso(future["epoch"]),
                                       "observed_secondary_raan_deg":float(future["state"][FIELDS.index("raan")])}]}
        result = compare_holdout([future],model,baseline)
        self.assertEqual(result["n"],1)
        self.assertTrue(result["metrics"]["max_quadrature_refinement_delta_deg"] < 1e-5)
        changed = dict(baseline, details=[dict(baseline["details"][0],
                                              observed_secondary_raan_deg=131)])
        with self.assertRaisesRegex(ValueError,"diverges"):
            compare_holdout([future],model,changed)
        with self.assertRaisesRegex(ValueError,"epoch identity"):
            compare_holdout([future],model,
                            dict(baseline, details=[{"epoch_utc":"2099-01-01T00:00:00.000000Z"}]))
        with self.assertRaisesRegex(ValueError,"leakage"):
            compare_holdout([self.fit[-1]],model,baseline)


if __name__ == "__main__":
    unittest.main()
