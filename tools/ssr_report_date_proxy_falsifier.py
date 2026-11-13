#!/usr/bin/env python3
"""Exact falsification of an affine *publication-date proxy*, not orbital dynamics."""
from __future__ import annotations

import argparse
from datetime import date
from fractions import Fraction
import json
from pathlib import Path

from ssr_post528_print_contrasts import HALF_PRINT_CENTIMIN, reports

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research/statistics/ssr_report_date_proxy_C241.json"
DAYS = ("1963-11-30", "1963-12-15", "1963-12-31")
OBJECTS = ("1963-003A", "1963-003C")


def _rational(value: Fraction) -> dict:
    """Use exact integers in exported certificates; never round floats."""
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def affine_report_date_test(days: tuple[str, str, str],
                            centers: tuple[int, int, int],
                            half_print_width: int = HALF_PRINT_CENTIMIN) -> dict:
    """Test existence of any affine interpolation through three interval cells.

    Each center is in centiminutes. The interval is conditional solely on
    decimal printing, not instrument calibration. Dates are a FALSE proxy for
    observation epochs and are never interpreted as an orbital clock.
    """
    if len(days) != 3 or len(centers) != 3:
        raise ValueError("three dated printed cells required")
    if not all(type(x) is int and x > 0 for x in centers):
        raise ValueError("positive integer centiminute centers required")
    if type(half_print_width) is not int or half_print_width < 0:
        raise ValueError("nonnegative integer print half-width required")
    t0, t1, t2 = (date.fromisoformat(day) for day in days)
    if not t0 < t1 < t2:
        raise ValueError("strictly ordered distinct publication dates required")
    weight_last = Fraction((t1-t0).days, (t2-t0).days)
    predicted = (1-weight_last)*centers[0] + weight_last*centers[2]
    residual = Fraction(centers[1]) - predicted
    # For an internal interpolation, nonnegative endpoint weights sum to 1.
    # Each of two quantities (middle cell and endpoint interpolation) has
    # a <= half_print_width error: residual band is +/- 2*half_print_width.
    radius = 2*half_print_width
    lo, hi = residual-radius, residual+radius
    return {
        "report_dates_not_instrument_epochs": list(days),
        "printed_centiminutes": list(centers),
        "interpolation_weight_last": _rational(weight_last),
        "midpoint_minus_affine_interpolation_centiminutes": _rational(residual),
        "conditional_residual_interval_centiminutes": [_rational(lo), _rational(hi)],
        "affine_publication_date_proxy_feasible_under_rounding": lo <= 0 <= hi,
    }


def build(documents: dict | None = None) -> dict:
    source_reports = reports(documents)  # source SHA, exact dates and membership gates
    indexed = {row["report_date_not_observation_epoch"]: row
               for row in source_reports}
    selected = [indexed[day] for day in DAYS]
    if len({row["pdf_sha256"] for row in selected}) != 3:
        raise ValueError("expected three individually source-locked report PDFs")
    checks = {}
    for designator in OBJECTS:
        values = tuple(row["printed_centiminutes"][designator]
                       for row in selected)
        checks[designator] = affine_report_date_test(DAYS, values)
    return {
        "schema": "conde.ssr-report-date-affine-proxy/v1",
        "classification": "CONDITIONAL_DOCUMENTARY_FALSIFICATION_NOT_ORBITAL_ACCELERATION",
        "hypothesis_tested": "Affine printed period in report/publication date, assuming the reports themselves are instrument epochs (counterfactual, not established)",
        "source_rows": [
            {"report_date_not_observation_epoch": row["report_date_not_observation_epoch"],
             "occurrence": row["occurrence"], "pdf_sha256": row["pdf_sha256"],
             "source_family": row["source_family"]}
            for row in selected
        ],
        "printing_assumption": "Each one-decimal printed period differs from the compiled underlying number by at most 0.05 minute; not a sensor bound",
        "tests_by_designator": checks,
        "limits": {
            "instrumental_epoch_utc": None,
            "measurement_error_and_covariance": None,
            "rate_or_acceleration_of_orbit": "NOT_IDENTIFIED",
            "source_independence": "NOT_ESTABLISHED_SHARED_NASA_NORAD_LINEAGE",
            "historical_mcmc": "NOT_RUN",
            "reentry_or_conde_exclusion": "NOT_AUTHORIZED",
            "active_physical_constraint": False,
            "next_discriminant": "Primary object-dated tracking times and frame/covariance to replace the counterfactual report-date proxy",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = (json.dumps(build(), indent=2, sort_keys=True, ensure_ascii=False)+"\n").encode()
    if args.check:
        if not OUT.is_file() or OUT.read_bytes() != content:
            raise SystemExit("source-locked report-date proxy certificate drift")
    else:
        OUT.write_bytes(content)


if __name__ == "__main__":
    main()
