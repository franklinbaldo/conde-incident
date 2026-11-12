#!/usr/bin/env python3
"""C241-P7: first-order nodal-period comparison for a 1963 NASA table.

This tests a compiled publication, NOT tracking epochs, TLE equivalence,
a terminal state, or a physical restriction on the 1963-003B reentry.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

from tle_nasa_ssr_oct15_audit import validate_ledger

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "research/tle_custody/nasa_ssr_1963_oct15_C241-L12.json"
EARTH_EQUATORIAL_RADIUS_KM = 6378.137  # modern convention, not 1963 source
MU_EARTH_KM3_S2 = 398600.4418         # modern convention, not NASA document field
J2 = 1.08262668e-3                   # declared modern first-order parameter


def period_models_min(apogee_km: float, perigee_km: float, inclination_deg: float,
                      *, radius_km: float = EARTH_EQUATORIAL_RADIUS_KM,
                      mu_km3_s2: float = MU_EARTH_KM3_S2,
                      j2: float = J2) -> tuple[float, float]:
    """Kepler period and first-order secular J2 draconitic proxy, in minutes.

    Approximate u-dot = omega-dot + M-dot, treating printed apsidal altitudes
    as if they described mean elements; not a calibrated SGP4 forward model.
    """
    values = (apogee_km, perigee_km, inclination_deg, radius_km, mu_km3_s2, j2)
    if not all(math.isfinite(v) for v in values):
        raise ValueError("all physical inputs must be finite")
    if not (radius_km > 0 and mu_km3_s2 > 0 and 0 <= j2 < 1
            and 0 <= perigee_km <= apogee_km and 0 <= inclination_deg <= 180):
        raise ValueError("invalid orbital proxy parameters")
    a = radius_km + (apogee_km + perigee_km) / 2
    eccentricity = (apogee_km - perigee_km) / (2 * a)
    n_rad_s = math.sqrt(mu_km3_s2 / a**3)
    cos_i = math.cos(math.radians(inclination_deg))
    common = 0.75 * j2 * n_rad_s * (radius_km / a)**2
    omega_dot = common * (5 * cos_i**2 - 1) / (1 - eccentricity**2)**2
    mean_anomaly_dot = (n_rad_s + common * (3 * cos_i**2 - 1)
                        / (1 - eccentricity**2)**1.5)
    nodal_rate = omega_dot + mean_anomaly_dot
    if nodal_rate <= 0:
        raise ValueError("invalid nodal angular rate")
    return 2 * math.pi / n_rad_s / 60, 2 * math.pi / nodal_rate / 60


def evaluate(ledger: dict) -> dict:
    """Falsifiable, zero-fit numerical check of the pinned NASA catalog rows."""
    validate_ledger(ledger)
    results = []
    for row in ledger["catalog_rows"]:
        printed = float(row["nodal_period_min_printed"])
        kepler, j2_nodal = period_models_min(
            row["apogee_km_printed"],
            row["perigee_km_printed"],
            float(row["inclination_deg_printed"]),
        )
        results.append({
            "international_designator": row["international_designator"],
            "published_nodal_period_min": printed,
            "kepler_two_body_period_min": kepler,
            "j2_first_order_nodal_period_min": j2_nodal,
            "kepler_signed_pred_minus_printed_seconds": (kepler - printed) * 60,
            "j2_signed_pred_minus_printed_seconds": (j2_nodal - printed) * 60,
        })
    kepler_mae = math.fsum(
        abs(r["kepler_signed_pred_minus_printed_seconds"]) for r in results
    ) / len(results)
    j2_mae = math.fsum(
        abs(r["j2_signed_pred_minus_printed_seconds"]) for r in results
    ) / len(results)
    return {
        "question": "Do two-body or first-order J2 nodal-period proxies match NASA Oct 1963 3A/3B/3C printed values?",
        "source_record": "C241-L12",
        "source_ntrs": "19640000428",
        "source_pdf_sha256": ledger["source"]["sha256"],
        "source_page_printed": 5,
        "source_lineage": "NASA_1963_COMPILED_PUBLICATION_NOT_RAW_SENSOR",
        "fixed_modern_assumptions": {
            "earth_equatorial_radius_km": EARTH_EQUATORIAL_RADIUS_KM,
            "mu_km3_s2": MU_EARTH_KM3_S2,
            "j2_dimensionless": J2,
            "apogee_perigee_as_apsidal_altitudes": "ASSUMED_FOR_NUMERIC_CONTROL",
        },
        "fitted_parameters": 0,
        "samples_in_one_compiled_source": len(results),
        "target_not_an_independent_holdout": "1963-003B",
        "two_body_mae_seconds": kepler_mae,
        "j2_mae_seconds": j2_mae,
        "objects": results,
        "physical_orbit_domain_reduction": "NONE",
        "promoted_lean_constraint": False,
        "missing": "tracking epochs, historical nodal-period/altitude definition, calibrated sensor covariance, independent holdouts",
    }


def main() -> None:
    print(json.dumps(
        evaluate(json.loads(LEDGER.read_text(encoding="utf-8"))),
        ensure_ascii=False, sort_keys=True, indent=2,
    ))


if __name__ == "__main__":
    main()
