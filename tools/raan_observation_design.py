#!/usr/bin/env python3
"""Exact S1 gauge and discriminating-observation design; NO historical posterior.

Every candidate is a conditional experiment, never an observation from 1963.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from raan_lineage_identifiability import build_report, matrix_rank_exact, row_for_object

SCHEMA = "conde.raan-discriminating-observation-design/v1"
SOURCE = "research/statistics/raan_527_528_529_1963.json"
SPLIT = "research/statistics/raan_chronological_holdout_1963.json"
OBJECTS = ("527", "528", "529")
BASE_COLUMNS = ("phase_527", "phase_528", "phase_529", "offset_catalog")
BASE_ROWS = [row_for_object(obj) for obj in OBJECTS]


def _scenario(
    name: str,
    added_rows: list[tuple[int, ...]],
    *,
    new_uncalibrated_lineage: bool,
    type_of_evidence: str,
    independence_requirement: str,
) -> dict:
    """Exact tangent-space rank for a stated *additive* circular model.

    Rows are coefficients for phase_527/528/529, catalog bias and optionally
    a new unknown source offset. Absolute phase/offset rows are externally
    referenced; no actual historical anchor is asserted to exist.
    """
    columns = BASE_COLUMNS + (("offset_new_lineage",) if new_uncalibrated_lineage else ())
    baseline = [r + ((0,) if new_uncalibrated_lineage else ()) for r in BASE_ROWS]
    if any(len(r) != len(columns) for r in added_rows):
        raise ValueError("observation design dimension mismatch")
    rows = baseline + added_rows
    rank = matrix_rank_exact(rows)
    base_rank = matrix_rank_exact(baseline)
    gauge = (1, 1, 1, -1) + ((-1,) if new_uncalibrated_lineage else ())
    still_invariant = all(sum(x * y for x, y in zip(row, gauge)) == 0 for row in rows)
    deficiency = len(columns) - rank
    # With the specified three object phases and one bias per source, the
    # baseline has exactly one global rotational gauge, including added sources.
    if (deficiency == 0) == still_invariant:
        raise AssertionError("rank and explicit circular gauge disagree")
    return {
        "candidate": name,
        "candidate_status": "COUNTERFACTUAL_NO_OBSERVATION_RECOVERED",
        "type": type_of_evidence,
        "required_independence_or_calibration": independence_requirement,
        "parameter_columns": list(columns),
        "new_observation_rows": [list(x) for x in added_rows],
        "rank_before_candidate": base_rank,
        "rank_after_candidate": rank,
        "parameter_count_after": len(columns),
        "remaining_nullity": deficiency,
        "gauge_vector": list(gauge),
        "global_absolute_phase_identified": not still_invariant,
        "interpretation": (
            "Absolute phase locally identifiable ONLY IF this proposed "
            "absolute measurement and its reference are independently validated."
            if not still_invariant else
            "Absolute phase remains free: observations do not remove the common S1 gauge."
        ),
    }


def candidate_designs() -> list[dict]:
    return [
        _scenario(
            "additional_catalog_epochs_528", [(0, 1, 0, 1)],
            new_uncalibrated_lineage=False,
            type_of_evidence="same_lineage_repeated_catalog_row",
            independence_requirement="same documentary lineage; not another sensor",
        ),
        _scenario(
            "cross_object_relative_raan_528_minus_529", [(0, 1, -1, 0)],
            new_uncalibrated_lineage=False,
            type_of_evidence="relative_contrast_only",
            independence_requirement="relative phase does not supply inertial absolute reference",
        ),
        _scenario(
            "new_lineage_only_528_free_bias", [(0, 1, 0, 0, 1)],
            new_uncalibrated_lineage=True,
            type_of_evidence="new_sensor_or_archive_with_unknown_offset",
            independence_requirement="prove new lineage; independently estimate its unknown angular zero",
        ),
        _scenario(
            "new_lineage_all_three_free_bias",
            [(1, 0, 0, 0, 1), (0, 1, 0, 0, 1), (0, 0, 1, 0, 1)],
            new_uncalibrated_lineage=True,
            type_of_evidence="multiple_objects_new_lineage_unknown_offset",
            independence_requirement="prove independently measured source; zero-point remains unknown",
        ),
        _scenario(
            "calibrated_absolute_phase_528", [(0, 1, 0, 0)],
            new_uncalibrated_lineage=False,
            type_of_evidence="independent_absolute_inertial_raan_reference",
            independence_requirement=(
                "document original calibrated sensor, epoch, inertial frame, "
                "catalog-mean mapping, nonzero error precision and covariance"
            ),
        ),
        _scenario(
            "independent_calibration_catalog_offset", [(0, 0, 0, 1)],
            new_uncalibrated_lineage=False,
            type_of_evidence="externally_calibrated_documentary_angular_zero",
            independence_requirement="source-independent calibration with frame/epoch and precision",
        ),
    ]


def report(raw: bytes, frozen: bytes) -> dict:
    history = build_report(raw, frozen)  # strict provenance and pinned membership
    if history["per_split"]["fit"]["exact_rational_rank"] != 3:
        raise ValueError("baseline rank changed")
    designs = candidate_designs()
    if [d["global_absolute_phase_identified"] for d in designs] != [
        False, False, False, False, True, True
    ]:
        raise AssertionError("counterfactual identification classification changed")
    return {
        "schema": SCHEMA,
        "inference_classification": "STRUCTURAL_AND_COUNTERFACTUAL_ONLY",
        "source": {"path": SOURCE, "sha256": hashlib.sha256(raw).hexdigest(),
                   "lineage": history["source"]["lineage"],
                   "occurrence_ids": ["C25#1", "C179#1", "C180#1", "C181#1", "C241-L3"],
                   "historical_independent_angular_anchor": None},
        "frozen_holdout": {
            "path": SPLIT, "sha256": hashlib.sha256(frozen).hexdigest(),
            "retrospective_not_blinded": True,
            "unique_epochs": {
                part: history["per_split"][part]["unique_catalogue_epochs"]
                for part in ("fit", "validation", "evaluation")
            },
            "gauge_rank_every_block": {
                part: history["per_split"][part]["exact_rational_rank"]
                for part in ("fit", "validation", "evaluation")
            },
        },
        "scope": (
            "Exact global S1 shift symmetry for three free circular phases and "
            "one uncalibrated additive offset per documentary lineage, with "
            "frozen dynamics. Rank is LOCAL structural only; it cannot certify "
            "global identifiability of real orbital dynamics or geolocation."
        ),
        "candidates": designs,
        "priority_condition": (
            "Recover a truly independent calibrated absolute angular reference "
            "or offset calibration; repeated/relative/catalog observations may "
            "improve contrasts but cannot resolve absolute gauge."
        ),
        "non_data_prior_warning": (
            "A concentrated prior on a phase or bias may fix a sampling gauge "
            "but is NOT a new observation and is NOT identification by the data."
        ),
        "observation_available": False,
        "historical_error_covariance": None,
        "historical_forward_operator_validated": False,
        "prior_calibrated": False,
        "historical_mcmc": "NOT_RUN",
        "holdout_predictive_score": "NOT_RUN",
        "admissible_geographic_domain_reduction": "NOT_EVALUABLE",
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--split", type=Path, required=True)
    out = p.add_mutually_exclusive_group(required=True)
    out.add_argument("--output", type=Path)
    out.add_argument("--check", type=Path)
    a = p.parse_args()
    result = report(a.input.read_bytes(), a.split.read_bytes())
    payload = (json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()
    if a.check:
        if a.check.read_bytes() != payload:
            raise SystemExit("FAIL: discriminating-observation report differs from frozen replay")
        print("GAUGE_OBSERVATION_DESIGN_REPRODUCED", len(result["candidates"]))
    else:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_bytes(payload)


if __name__ == "__main__":
    main()
