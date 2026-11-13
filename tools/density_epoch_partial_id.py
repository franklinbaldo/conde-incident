#!/usr/bin/env python3
"""C241-P30: exact partial-identification bounds when common density drifts."""
import argparse
import hashlib
import json
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P29 = ROOT / "research/constraints/C241-P29_density_epoch_contrast.json"
OUTPUT = ROOT / "research/constraints/C241-P30_density_epoch_partial_id.json"


def fmt(value):
    return f"{value.numerator}/{value.denominator}"


def gamma_interval(delta_h, contrast, *, kappa0=None, kappa1=None, error=None):
    """Intersection of |contrast + delta_h*gamma| <= K with gamma>=0.

    Unbounded unknown distortion is represented by None for all three budgets.
    All other inputs must be exact Fractions (not floats).
    """
    delta_h, contrast = F(delta_h), F(contrast)
    if (kappa0, kappa1, error) == (None, None, None):
        return {"status": "UNIDENTIFIED", "gamma_min": "0/1",
                "gamma_max": None, "H_km": "NOT_BOUNDED"}
    if any(x is None for x in (kappa0, kappa1, error)):
        raise ValueError("all three distortion/error bounds required")
    if any(not isinstance(x, F) or x < 0
           for x in (kappa0, kappa1, error)):
        raise ValueError("budgets must be nonnegative exact fractions")
    K = kappa0 + kappa1 + error
    if delta_h == 0:
        return {"status": "UNIDENTIFIED" if abs(contrast) <= K else "REJECTED",
                "gamma_min": "0/1" if abs(contrast) <= K else None,
                "gamma_max": None, "H_km": "NOT_BOUNDED" if abs(contrast) <= K else None}
    endpoints = sorted(((-contrast - K) / delta_h,
                        (-contrast + K) / delta_h))
    low, high = endpoints
    if high < 0:
        return {"status": "REJECTED", "gamma_min": None,
                "gamma_max": None, "H_km": None}
    low = max(F(0), low)
    if high == 0:
        return {"status": "ONLY_INFINITE_H", "gamma_min": "0/1",
                "gamma_max": "0/1", "H_km": "ONLY_INFINITY"}
    if low == high:
        status = "POINT_IDENTIFIED_CONDITIONALLY"
    elif low == 0:
        status = "NO_FINITE_UPPER_BOUND_H"
    else:
        status = "PARTIALLY_IDENTIFIED"
    H = (f"[{fmt(1/high)},{fmt(1/low)}]" if low > 0
         else f"[{fmt(1/high)},INFINITY)")
    return {"status": status, "gamma_min": fmt(low),
            "gamma_max": fmt(high), "H_km": H}


def report():
    raw = P29.read_bytes()
    previous = json.loads(raw)
    if previous.get("id") != "C241-P29" or previous.get("active_constraint") is not False:
        raise ValueError("C241-P29 must be source-linked and inactive")
    delta = previous["exact_rank_diagnostic"]["altitude_interaction_km"]
    if delta != 30 or previous["interaction"]["coefficient_of_inverse_scale_height_km"] != -30:
        raise ValueError("unexpected source contrast; no silent redefinition")
    # All synthetic inputs are explicit and exact. No historical measurements.
    C = F("-0.6")
    zero = F(0)
    bounded = {"kappa0": F("0.1"), "kappa1": F("0.1"),
               "error": F("0.05")}
    return {
        "id": "C241-P30",
        "status": "SYNTHETIC_PARTIAL_IDENTIFICATION_NO_HISTORICAL_FIT",
        "base_model": {"path": P29.relative_to(ROOT).as_posix(),
                       "sha256": hashlib.sha256(raw).hexdigest()},
        "operator": "C=-Delta_h*gamma+(d1-d0)+e; gamma=1/H>=0; |dt|<=kappat; |e|<=error",
        "synthetic_input": {"Delta_h_km": delta, "C_log_units": fmt(C),
                            "true_gamma_for_test_only_per_km": "1/50"},
        "experiments": {
            "exact_shared_epoch_q": gamma_interval(delta, C, kappa0=zero,
                                                    kappa1=zero, error=zero),
            "bounded_spatial_temporal_heterogeneity": {
                "assumed_bounds_log_units": {k: fmt(v) for k, v in bounded.items()},
                "result": gamma_interval(delta, C, **bounded),
            },
            "bounded_but_zero_gamma_allowed":
                gamma_interval(delta, C, kappa0=F("0.3"),
                               kappa1=F("0.3"), error=zero),
            "unbounded_object_specific_density": gamma_interval(delta, C),
            "no_altitude_interaction": gamma_interval(0, C, **bounded),
            "falsification_example": gamma_interval(delta, F("0.6"),
                                                     kappa0=zero, kappa1=zero,
                                                     error=zero),
        },
        "conditions": [
            "Four independent-calibration-eligible drag observables in two objects and two actual epochs.",
            "Each satellite has constant positive ballistic coefficient across the two epochs.",
            "Differential log density at each epoch has externally calibrated finite bound.",
            "Combined contrast error bound accounts for correlation and orbital-model residuals.",
            "No bound in this report comes from 1963; all numerics are counterfactual.",
            "The fourth cell is used to identify gamma, not reserved as holdout.",
        ],
        "holdout": "NOT_AVAILABLE",
        "NORAD_528_ballistic_identification": "UNIDENTIFIED_NO_528_OBSERVATION",
        "historical_mcmc": "NOT_RUN",
        "historical_domain_reduction": "NOT_EVALUABLE",
        "active_constraint": False,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = p.parse_args()
    serialized = json.dumps(report(), ensure_ascii=False, indent=2) + "\n"
    if args.write:
        OUTPUT.write_text(serialized)
        print(f"WROTE {OUTPUT.relative_to(ROOT)}")
    elif args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text() != serialized:
            raise SystemExit("FAIL: C241-P30 manifest differs from reproducible result")
        print("PASS: C241-P30 exact partial-identification certificate")
    else:
        print(serialized, end="")


if __name__ == "__main__":
    main()
