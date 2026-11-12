#!/usr/bin/env python3
"""Exact conditional structural observability of circular RAAN phase/drift.

No physical orbit, catalogue noise, prior, likelihood or historical posterior.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
from pathlib import Path

from raan_lineage_identifiability import build_report, matrix_rank_exact, OBJECTS, SPLITS

SCHEMA = "conde.raan-temporal-gauge/v1"
SOURCE = "research/statistics/raan_527_528_529_1963.json"
SPLIT = "research/statistics/raan_chronological_holdout_1963.json"
REF = datetime(1963, 1, 1, tzinfo=timezone.utc)
MICROSECONDS_PER_DAY = 86_400_000_000
# Full model: three phases, three individual linear rates, common offset and its drift.
COLUMNS = (
    "phase_527", "phase_528", "phase_529",
    "rate_527_deg_day", "rate_528_deg_day", "rate_529_deg_day",
    "catalog_offset", "catalog_drift_deg_day",
)
PHASE_GAUGE = (1, 1, 1, 0, 0, 0, -1, 0)
RATE_GAUGE = (0, 0, 0, 1, 1, 1, 0, -1)
PHASE_528_ANCHOR = (0, 1, 0, 0, 0, 0, 0, 0)
RATE_528_ANCHOR = (0, 0, 0, 0, 1, 0, 0, 0)


def days_from_reference(epoch: str) -> Fraction:
    """UTC microsecond epochs, exactly rational days, no floating-point times."""
    if not isinstance(epoch, str) or not epoch.endswith("Z"):
        raise ValueError("expected ISO8601 UTC Z epoch")
    try:
        when = datetime.fromisoformat(epoch.replace("Z", "+00:00"))
    except (ValueError, OverflowError) as e:
        raise ValueError("invalid UTC epoch") from e
    if when.tzinfo != timezone.utc or when.year != 1963:
        raise ValueError("epoch must be UTC in 1963")
    delta = when - REF
    micros = (delta.days * 86_400 + delta.seconds) * 1_000_000 + delta.microseconds
    return Fraction(micros, MICROSECONDS_PER_DAY)


def model_row(norad: str, day: Fraction) -> tuple[Fraction, ...]:
    """Local design with a common undocumented source angular zero and drift."""
    if norad not in OBJECTS or not isinstance(day, Fraction):
        raise ValueError("invalid object or exact epoch")
    i = OBJECTS.index(norad)
    return tuple(
        [Fraction(int(k == i)) for k in range(3)]
        + [day if k == i else Fraction(0) for k in range(3)]
        + [Fraction(1), day]
    )


def certificate(rows: list[tuple[Fraction, ...]]) -> dict:
    """Exact ranks; anchors only hypothetical independent calibrated measurements."""
    if any(len(row) != 8 for row in rows):
        raise ValueError("8-column temporal RAAN model required")
    if not rows:
        raise ValueError("at least one observation required")
    if any(sum(x * y for x, y in zip(row, PHASE_GAUGE)) != 0 for row in rows):
        raise AssertionError("phase gauge was not preserved")
    if any(sum(x * y for x, y in zip(row, RATE_GAUGE)) != 0 for row in rows):
        raise AssertionError("rate gauge was not preserved")
    rank_constant = matrix_rank_exact([row[:7] for row in rows])
    rank_drift = matrix_rank_exact(rows)
    rank_phase = matrix_rank_exact(rows + [PHASE_528_ANCHOR])
    rank_rate = matrix_rank_exact(rows + [RATE_528_ANCHOR])
    rank_both = matrix_rank_exact(rows + [PHASE_528_ANCHOR, RATE_528_ANCHOR])
    return {
        "constant_catalog_offset": {"rank": rank_constant, "columns": 7,
                                    "nullity": 7 - rank_constant},
        "free_catalog_offset_and_drift": {"rank": rank_drift, "columns": 8,
                                         "nullity": 8 - rank_drift},
        "hypothetical_absolute_phase_528_only": {
            "rank": rank_phase, "columns": 8, "nullity": 8 - rank_phase,
        },
        "hypothetical_absolute_rate_528_only": {
            "rank": rank_rate, "columns": 8, "nullity": 8 - rank_rate,
        },
        "hypothetical_both_anchors_528": {
            "rank": rank_both, "columns": 8, "nullity": 8 - rank_both,
        },
        "gauge_phase_vector": list(PHASE_GAUGE),
        "gauge_rate_vector": list(RATE_GAUGE),
    }


def build(source_bytes: bytes, frozen_bytes: bytes) -> dict:
    history = build_report(source_bytes, frozen_bytes)
    manifest = json.loads(frozen_bytes)
    if manifest["unique_total"] != 119:
        raise ValueError("unexpected catalogue cardinality")
    per_split = {}
    for part in SPLITS:
        rows = []
        counts = {}
        distinct_days = {}
        for norad in OBJECTS:
            epochs = manifest["memberships"][norad][part]
            days = [days_from_reference(x) for x in epochs]
            if len(set(days)) != len(days):
                raise ValueError("duplicate UTC instants")
            counts[norad] = len(days)
            distinct_days[norad] = len(set(days))
            rows.extend(model_row(norad, t) for t in days)
        cert = certificate(rows)
        if len(rows) != history["per_split"][part]["unique_catalogue_epochs"]:
            raise ValueError("holdout split changed")
        per_split[part] = {
            "epochs_from_one_secondary_lineage": len(rows),
            "object_counts": counts,
            "distinct_epochs_by_object": distinct_days,
            "exact_structural_design": cert,
            "historical_likelihood": "NOT_CALIBRATED",
            "posterior_mcmc": "NOT_RUN",
        }
    all_rows = [
        model_row(norad, days_from_reference(epoch))
        for part in SPLITS for norad in OBJECTS
        for epoch in manifest["memberships"][norad][part]
    ]
    return {
        "schema": SCHEMA,
        "classification": "EXACT_CONDITIONAL_STRUCTURAL_LOCAL_IDENTIFIABILITY",
        "source": {"path": SOURCE, "sha256": hashlib.sha256(source_bytes).hexdigest(),
                   "occurrence_ids": ["C25#1", "C179#1", "C180#1", "C181#1", "C241-L3"],
                   "documentary_lineages": 1, "original_instrument_record": None},
        "holdout": {"path": SPLIT, "sha256": hashlib.sha256(frozen_bytes).hexdigest(),
                    "retrospective_not_blind": True, "not_instrumentally_independent": True},
        "time_reference": "1963-01-01T00:00:00Z",
        "exact_time_unit": "integer UTC microseconds / 86400000000, days",
        "model_hypothesis": (
            "Omega_j(t)=wrap(F_j(t)+phase_j+rate_j*t+catalog_offset"
            "+catalog_drift*t). F_j is fixed but NOT provided, fitted or validated."
        ),
        "parameter_columns": list(COLUMNS),
        "all_epochs": {"unique": len(all_rows),
                       "exact_structural_design": certificate(all_rows)},
        "per_split": per_split,
        "warnings": [
            "The full model is only a local additive angular design; wrapped observations can have global rate aliases.",
            "If catalogue drift is unconstrained, rates have a second gauge even with numerous epochs.",
            "A phase-only anchor does not identify a shared undocumented rate drift, nor vice versa.",
            "The sole 527 validation epoch cannot separately identify its phase and rate in validation alone.",
            "Rank does not quantify signal/noise, physical dynamics, errors, selection or posterior uncertainty.",
            "All anchors here are COUNTERFACTUAL; no independent calibrated instrument is claimed.",
            "The split was designed after inspecting the data and shares the documentary lineage.",
        ],
        "required_to_upgrade": [
            "Castor: physical forward operator for mean TLE RAAN, frame/epoch-compatible",
            "Tartaruga: authenticated instrument, independent absolute angle/time calibration and uncertainty",
            "Documented angular error covariance and reporting/selection model",
            "Pre-registered true independent holdout before calibrated inference",
        ],
        "priors_historical": None,
        "error_model_historical": None,
        "historical_posterior": "NOT_RUN",
        "geographic_domain_reduction": "NOT_EVALUABLE",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--split", type=Path, required=True)
    dest = parser.add_mutually_exclusive_group(required=True)
    dest.add_argument("--output", type=Path)
    dest.add_argument("--check", type=Path)
    args = parser.parse_args()
    result = build(args.input.read_bytes(), args.split.read_bytes())
    data = (json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()
    if args.check:
        if args.check.read_bytes() != data:
            raise SystemExit("FAIL: temporal-gauge replay differs from frozen output")
        print("TEMPORAL_GAUGE_REPRODUCED", result["all_epochs"]["unique"])
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(data)


if __name__ == "__main__":
    main()
