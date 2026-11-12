"""C241-P2 controls for fit-only J2, strict source agreement, and no refit."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from raan_frozen_j2_holdout import (  # noqa: E402
    align_rows, compare, frozen_j2_rate, j2_predict, MAX_RAAN_SERIALIZATION_DELTA_DEG,
)
from raan_frozen_trend_holdout import fit_only
from cross_object_epoch_support import FIELDS


def make_state(raan="123.0", inclination="81.8615", e="0.0084200", n="15.749"):
    values = {"inclination": inclination, "raan": raan,
              "eccentricity": e, "mean_motion": n}
    return tuple(values.get(field, "0") if field != "intl_designator" else "1963-003B"
                 for field in FIELDS)


class FrozenJ2Holdout(unittest.TestCase):
    def setUp(self):
        self.epoch = datetime(1963, 1, 1, tzinfo=timezone.utc)
        self.fit = [(self.epoch+timedelta(days=i), 123.0-i*1.1) for i in range(3)]
        self.rows = [{"epoch": self.fit[-1][0], "source_rows": [42],
                      "state": make_state(raan=str(self.fit[-1][1]))}]

    def test_fits_last_state_only_and_has_physical_units(self):
        anchor = frozen_j2_rate(self.fit, self.rows)
        self.assertEqual(anchor["source_rows"], [42])
        self.assertEqual(anchor["anchor_epoch_utc"], "1963-01-03T00:00:00.000000Z")
        self.assertLess(anchor["rate_deg_per_day"], 0)
        self.assertGreater(anchor["rate_deg_per_day"], -2)

    def test_different_future_state_does_not_change_j2(self):
        anchor = frozen_j2_rate(self.fit, self.rows)
        future = {"epoch": self.epoch+timedelta(days=20),
                  "source_rows": [43], "state": make_state(n="25")}
        again = frozen_j2_rate(self.fit, self.rows + [future])
        self.assertEqual(anchor, again)

    def test_does_not_choose_nearest_future_state(self):
        with self.assertRaisesRegex(ValueError, "missing/ambiguous"):
            frozen_j2_rate(self.fit, [dict(self.rows[0], epoch=self.epoch+timedelta(days=10))])
        with self.assertRaisesRegex(ValueError, "missing/ambiguous"):
            frozen_j2_rate(self.fit, self.rows+self.rows)

    def test_raan_serialization_not_treated_as_sensor_sigma(self):
        self.assertLess(MAX_RAAN_SERIALIZATION_DELTA_DEG, 0.001)
        fake = [dict(self.rows[0], state=make_state(raan="140"))]
        with self.assertRaisesRegex(ValueError, "RAAN mismatch"):
            frozen_j2_rate(self.fit, fake)

    def test_horizon_and_circular_residual(self):
        model = fit_only(self.fit)
        anchor = frozen_j2_rate(self.fit, self.rows)
        future = self.epoch+timedelta(days=30)
        pred = j2_predict(anchor, future, epoch=model["last_fit_epoch"])
        result = compare([(future, pred)], anchor, model)
        self.assertAlmostEqual(result["models"]["last_fit_j2_proxy"]["mae_deg"], 0)
        self.assertEqual(result["n"], 1)
        self.assertIn("fitonly_linear", result["models"])

    def test_reject_leakage_and_empty_test(self):
        model = fit_only(self.fit)
        anchor = frozen_j2_rate(self.fit, self.rows)
        with self.assertRaisesRegex(ValueError, "leakage"):
            compare([(self.fit[-1][0], 120)], anchor, model)
        with self.assertRaisesRegex(ValueError, "empty"):
            compare([], anchor, model)

    def test_invalid_physical_state_fails(self):
        for kwargs in ({"e": "1"}, {"n": "0"}, {"inclination": "190"}):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    frozen_j2_rate(self.fit, [dict(self.rows[0],
                        state=make_state(raan=str(self.fit[-1][1]), **kwargs))])


if __name__ == "__main__":
    unittest.main()
