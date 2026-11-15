#!/usr/bin/env python3
"""R67: exact decimal print-cell feasibility, not a historical identity fit.

A comparison between a NASA nodal-period table and a secondary TLE proxy is
not coepocal or definition-matched. The bin test below is conditional only.
"""
from __future__ import annotations

import argparse
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path

EXPECTED = {
    "period_minutes": ("nodal_period_minutes", "period_minutes_from_mean_motion", "89.7", "0.1"),
    "inclination_degrees": ("inclination_degrees", "inclination_degrees", "82.15", "0.01"),
    "apogee_km": ("apogee_km", "kepler_apogee_proxy_km", "263", "1"),
    "perigee_km": ("perigee_km", "kepler_perigee_proxy_km", "254", "1"),
}
EXPECTED_SHA = "fe5183940081fbbfe1e791b8cf47c1ac2c08ecad0c17f5d54d7cac83fb5992b2"
PARQUET_SHA = "c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09"


def number(value: object) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (str, float, int)):
        raise ValueError("invalid numeric value")
    try:
        d = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError("invalid numeric value") from exc
    if not d.is_finite():
        raise ValueError("nonfinite numeric value")
    return d


def audit(r65: dict) -> dict:
    if not isinstance(r65, dict) or r65.get("schema") != "conde.c241-omega1-308-numeric-fingerprint-r65/v1":
        raise ValueError("wrong R65 schema")
    sources = r65.get("sources", {})
    if (sources.get("primary_ssr_sha256") != EXPECTED_SHA
            or sources.get("secondary_tle_sha256") != PARQUET_SHA
            or sources.get("lineage_independence_established") is not False):
        raise ValueError("provenance or lineage promoted")
    printed, cand, caveats, inference = (r65.get(k, {}) for k in
                                         ("printed_row", "candidate", "comparison_caveats", "inference"))
    if (printed.get("name") != "OMEGA 1" or printed.get("norad_id_printed") is not None
            or printed.get("report_as_of_utc_NOT_OBSERVATION") != "1963-10-15T12:00:00Z"
            or cand.get("norad_id") != 308
            or cand.get("last_pre_cutoff_epoch_utc") != "1963-10-14T23:23:55.702464Z"
            or cand.get("pre_cutoff_epochs") != 44
            or cand.get("excluded_at_or_after_cutoff") != 8
            or caveats.get("nodal_period_equals_tle_kepler_period") is not False
            or caveats.get("ssr_printed_elements_same_instrument_epoch_as_tle") is not False
            or caveats.get("apogee_perigee_kepler_proxy_equals_ssr_definition") is not False
            or caveats.get("candidate_cohort_exhaustive") is not False
            or inference.get("historical_mcmc") != "NOT_RUN"
            or inference.get("active_constraint_528") is not False
            or inference.get("identity_probability") is not None):
        raise ValueError("R65 preconditions or scientific limits violated")

    bins = {}
    for name, (printed_key, candidate_key, literal, quantum) in EXPECTED.items():
        p, q = Decimal(literal), Decimal(quantum)
        if number(printed.get(printed_key)) != p:
            raise ValueError("printed precision/value drift: " + name)
        v = number(cand.get(candidate_key))
        lower, upper = p - q / 2, p + q / 2
        inside = lower <= v < upper
        gap = lower - v if v < lower else (v - upper if v >= upper else Decimal(0))
        bins[name] = {
            "printed": literal, "printed_step": quantum,
            "conditional_rounding_cell_lower": str(lower),
            "conditional_rounding_cell_upper_exclusive": str(upper),
            "candidate_secondary_proxy": str(v),
            "inside_conditional_cell": inside,
            "minimum_conditional_bridge_magnitude": str(gap),
            "unit": "minutes" if name == "period_minutes" else
                    ("degrees" if name == "inclination_degrees" else "km"),
        }
    mismatch = [k for k, v in bins.items() if not v["inside_conditional_cell"]]
    return {
        "schema": "conde.c241.omega-print-quantization-r67/v1",
        "conditional_hypothesis": "same_epoch_same_observable_same_definition_round_to_nearest",
        "hypothesis_historically_justified": False,
        "mismatches_under_hypothesis": mismatch,
        "comparisons": bins,
        "scientific_interpretation": {
            "rounding_only_four_way_match": len(mismatch) == 0,
            "orbit_identity_rejected": False,
            "orbit_identity_established": False,
            "independent_terminal_holdouts": 0,
            "actual_utc_terminal_time": None,
            "terminal_sigma_hours": None,
            "identity_probability": None,
            "active_constraint_528": False,
            "historical_mcmc": "NOT_RUN",
            "impact_geography": None,
            "needed_bridges": ["SSR element epoch", "nodal-period/SGP4 mapping",
                               "apogee-perigee definition", "contemporaneous NORAD crosswalk",
                               "instrumental covariance"],
        },
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--r65", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    result = audit(json.loads(args.r65.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("R67: conditional rounding mismatch; identity and MCMC NOT_INFERRED")


if __name__ == "__main__":
    main()
