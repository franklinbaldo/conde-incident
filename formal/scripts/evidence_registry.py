#!/usr/bin/env python3
"""Check all historical matrix row identities and export conservative contracts.

This script reads the fixed matrix snapshot. It does NOT authenticate a source,
re-run orbital calculations, or infer physical constraints from narrative text.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

MATRIX_SHA1 = "a7978c3a75a153b16ab70118a92c434bba674cb7"
MATRIX_COMMIT = "38ee0f01134f6a1ee07c9346945d058d2ad3ce0b"
MATRIX_PATH = "research/evidence_matrix_C001-C238_2026-11-11.md"
SOURCE_REPO = "https://github.com/franklinbaldo/conde-incident"
ROW = re.compile(r"^\|\s*(?:\*\*)?(C[0-9]+)(?:\*\*)?\s*\|")
HEADER = "import Conde1963.DocumentaryDay\n\n/-!\n# Typed identity AND explicit uncertainty of all 241 matrix occurrences\n\nNo row directly establishes a physical decay day, hour, location or impact.\nC131/C197 refer to ONE historical catalogue publication. Only the\nDOCUMENTARY statement of a catalogued date is proven from the source.\nC01 preserves the radio report as a report, not an observed crater.\n\nAll other rows explicitly say \"individual uncertainty not yet assessed\nin this formal transfer\", not \"false\" or \"unverified evidence\".\nNo documentary row in this registry is a hard physical predicate.\n-/\n\nset_option maxRecDepth 4096\n\nnamespace Conde1963\n\ninductive RowPhysicalRole where\n  | contextOnly\n  | nasaReportedDecayDay\n  deriving Repr, DecidableEq\n\ninductive EpistemicUncertainty where\n  | requiresIndividualAssessment\n  | reportExistsPhysicalOccurrenceUnverified\n  | reportedCatalogueDayActualDayUnknown\n  deriving Repr, DecidableEq\n\nstructure MatrixEvidenceRef where\n  labelNumber : Nat\n  occurrence : Nat\n  matrixLine : Nat\n  role : RowPhysicalRole\n  uncertainty : EpistemicUncertainty\n  deriving Repr, DecidableEq\n\ndef evidenceMatrixRows : List MatrixEvidenceRef := [\n"
FOOTER = "]\n\n/-- Membership in a catalogue of documentary claims imposes NO physical\n    restriction until separately reviewed and explicitly admitted with\n    a calibrated observational error model. -/\ndef acceptedMatrixPredicate\n    (_row : MatrixEvidenceRef) (_candidate : ReentryCandidate) : Prop :=\n  True\n\ndef AllMatrixEvidence (candidate : ReentryCandidate) : Prop :=\n  ∀ row, row ∈ evidenceMatrixRows → acceptedMatrixPredicate row candidate\n\ntheorem evidence_matrix_row_count : evidenceMatrixRows.length = 241 := by decide\n\ntheorem nasa_matrix_rows_explicitly_mark_uncertainty :\n    (⟨131, 1, 502, .nasaReportedDecayDay,\n       .reportedCatalogueDayActualDayUnknown⟩ : MatrixEvidenceRef) ∈ evidenceMatrixRows ∧\n    (⟨197, 1, 905, .nasaReportedDecayDay,\n       .reportedCatalogueDayActualDayUnknown⟩ : MatrixEvidenceRef) ∈ evidenceMatrixRows := by\n  decide\n\ntheorem tupi_report_is_not_ground_observation :\n    (⟨1, 1, 19, .contextOnly,\n       .reportExistsPhysicalOccurrenceUnverified⟩ : MatrixEvidenceRef) ∈ evidenceMatrixRows := by\n  decide\n\ntheorem every_row_is_nonphysical_without_additional_premises\n    (candidate : ReentryCandidate) :\n    AllMatrixEvidence candidate := by\n  intro row _\n  trivial\n\n/-- Even an illustrated off-day state survives documentary indexing.\n    This is an epistemic countermodel, not a historical prediction. -/\ntheorem matrix_does_not_force_nasa_reported_day :\n    AllMatrixEvidence inventedOffDayExample ∧\n    ¬ PhysicalDayMatchesCatalogue inventedOffDayExample := by\n  exact ⟨every_row_is_nonphysical_without_additional_premises _, by\n    simp [PhysicalDayMatchesCatalogue, inventedOffDayExample, NasaCatalogueDay]⟩\n\ntheorem full_matrix_does_not_identify_region :\n    ¬ UniquelyIdentifiesRegion AllMatrixEvidence (fun _ => True) := by\n  apply two_admissible_regions_preclude_unique\n    AllMatrixEvidence (fun _ => True) condeCandidate anotherCandidate\n  · exact ⟨every_row_is_nonphysical_without_additional_premises _, True.intro⟩\n  · exact ⟨every_row_is_nonphysical_without_additional_premises _, True.intro⟩\n  · exact date_alone_does_not_identify_place.2.2\n\nend Conde1963\n"


class InventoryError(ValueError):
    """Matrix identity changed or expected evidence was lost."""


def parse_rows(data: bytes) -> list[dict]:
    try:
        lines = data.decode("utf-8").splitlines()
    except UnicodeDecodeError as exc:
        raise InventoryError("matrix must be UTF-8") from exc
    rows = []
    seen: dict[int, int] = {}
    section = ""
    for line_number, line in enumerate(lines, 1):
        if line.startswith("## "):
            section = line[3:].strip()
        m = ROW.match(line)
        if m is None:
            continue
        number = int(m.group(1)[1:])
        occurrence = seen.get(number, 0) + 1
        seen[number] = occurrence
        rows.append({
            "number": number,
            "occurrence": occurrence,
            "line": line_number,
            "role": "nasaReportedDecayDay" if number in (131, 197) else "contextOnly",
            "uncertainty": (
                "reportExistsPhysicalOccurrenceUnverified" if number == 1
                else "reportedCatalogueDayActualDayUnknown" if number in (131, 197)
                else "requiresIndividualAssessment"
            ),
            "row_markdown": line,
            "section": section,
        })
    return rows


def audit(data: bytes, rows: list[dict], *, strict_hash: bool = True) -> dict:
    actual = hashlib.sha1(
        b"blob " + str(len(data)).encode("ascii") + b"\0" + data
    ).hexdigest()
    if strict_hash and actual != MATRIX_SHA1:
        raise InventoryError(
            f"matrix blob changed ({actual} != {MATRIX_SHA1}); "
            "review new evidence and repin explicitly"
        )
    counts: dict[int, int] = {}
    for r in rows:
        n = r["number"]
        counts[n] = counts.get(n, 0) + 1
        if r["occurrence"] != counts[n]:
            raise InventoryError(f"invalid occurrence for C{n}")
        if r["role"] != ("nasaReportedDecayDay" if n in (131, 197) else "contextOnly"):
            raise InventoryError(f"unreviewed physical promotion at C{n}")
        expected_uncertainty = (
            "reportExistsPhysicalOccurrenceUnverified" if n == 1
            else "reportedCatalogueDayActualDayUnknown" if n in (131, 197)
            else "requiresIndividualAssessment"
        )
        if r.get("uncertainty") != expected_uncertainty:
            raise InventoryError(f"unreviewed epistemic uncertainty promotion at C{n}")
    if len(rows) != 241 or set(counts) != set(range(1, 239)):
        raise InventoryError("matrix must have 241 rows covering C01-C238")
    if {n: count for n, count in counts.items() if count != 1} != {
        44: 2, 45: 2, 46: 2,
    }:
        raise InventoryError("C44-C46 collision identities must remain distinct")
    anchors = [(131, 1, 502), (197, 1, 905)]
    for n, occ, line in anchors:
        if not any(r["number"] == n and r["occurrence"] == occ
                   and r["line"] == line for r in rows):
            raise InventoryError(f"NASA anchor C{n} line {line} changed")
    return {
        "status": "MATRIX_IDENTITY_PASS_ONLY",
        "blob_sha1": actual,
        "occurrences": len(rows),
        "unique_labels": len(counts),
        "collision_labels": ["C44", "C45", "C46"],
        "catalogued_day_hypothesis_rows": ["C131#1", "C197#1"],
        "physical_day_accepted_as_fact": False,
        "uncertainty_requires_individual_review": sum(
            r["uncertainty"] == "requiresIndividualAssessment" for r in rows
        ),
        "historical_source_authentication": "NOT_RUN",
        "original_154_proposition_lean_zip": "NOT_RUN",
        "physical_orbit_holdout": "NOT_RUN",
    }


def render_lean(rows: list[dict]) -> str:
    body = "".join(
        f'  ⟨{r["number"]}, {r["occurrence"]}, {r["line"]}, .{r["role"]}, .{r["uncertainty"]}⟩,\n'
        for r in rows
    )
    return HEADER + body + FOOTER



def outcome_interface() -> dict:
    """Typed *empty* handoff to Castor, not a fitted dynamics result.

    These are proof-obligation names in the compiled Lean kernel.
    A simulator must independently supply a physical model, uncertainty
    bounds, source identity, holdout checks and a nonempty feasible domain.
    Finite-search exhaustion is never global physical contradiction.
    """
    return {
        "version": 1,
        "kind": "CONDITIONAL_OUTCOME_PROOF_OBLIGATIONS_NOT_OBSERVATIONS",
        "lean_module": "Conde1963/Outcome.lean",
        "current_result": None,
        "calibrated_model": None,
        "numerical_impact_window": None,
        "required_inputs": [
            "source_matrix_ids_with_occurrence_and_pinned_citation",
            "independently_reviewed_provenance_and_chain",
            "evidence_uncertainty_and_physical_mapping",
            "justified_accepted_constraints_not_exploratory_scenarios",
            "nonempty_admissible_domain_with_strict_reduction_witness",
            "documented_orbit_model_units_epochs_error_and_holdouts",
            "global_coverage_proof_or_explicit_finite_grid_scope",
            "ground_impact_model_distinct_from_orbital_decay",
        ],
        "conditional_outcomes": [
            {
                "code": "CONTRADICTORY_PREMISES",
                "lean": "not HasCandidate",
                "scope": "global_model_only",
                "warning": "An empty finite grid is NOT proof of global contradiction.",
            },
            {
                "code": "CONDE_FORCED",
                "lean": "ForcesConde",
                "scope": "nonempty_admissible_model_only",
                "warning": "Every candidate must predict a ground impact in Conde.",
            },
            {
                "code": "CONDE_EXCLUDED",
                "lean": "ExcludesConde",
                "scope": "nonempty_admissible_model_only",
                "warning": "No impact in Conde does NOT establish an impact elsewhere.",
            },
            {
                "code": "OTHER_WINDOW",
                "lean": "IdentifiesOtherWindow",
                "scope": "nonempty_admissible_model_only",
                "warning": "Requires a predicted impact for every survivor and proven geographic disjointness from Conde.",
            },
            {
                "code": "INDETERMINATE",
                "lean": "MixedCondeOutcomes",
                "scope": "sufficient_mixed_outcomes_witness_not_exhaustive",
                "warning": "Other unresolved cases exist; the predicate is sufficient, not necessary.",
            },
        ],
    }




def enclosure_interface() -> dict:
    """Castor handoff for *conditional* numerical error envelopes.

    A geographic verdict needs a nonempty GLOBAL feasible domain, a sound
    enclosure for every survivor and an independently established ground-
    impact audit. Neither a generated proof template nor Boolean status
    declarations certify model calibration or historical observations.
    """
    return {
        "version": 1,
        "kind": "MODEL_ENCLOSURE_OBLIGATIONS_NOT_NUMERICAL_RESULTS",
        "lean_module": "Conde1963/Enclosures.lean",
        "current_result": None,
        "event_type": None,
        "numerical_epoch_window_utc": None,
        "numerical_spatial_enclosure": None,
        "global_parameter_domain_verified": False,
        "ground_impact_audit_verified": False,
        "historical_input_custody_verified": False,
        "independent_holdout_verified": False,
        "numerical_error_coverage_verified": False,
        "original_154_151_corpus_import": "NOT_RUN",
        "ground_impact_gate": "GroundImpactAdmissible",
        "enclosure_soundness": "ImpactEnvelope.soundForPredictions",
        "mandatory_proof_obligations": [
            "ground_impact_gate_independently_justified_not_claimed_by_bool_alone",
            "source_provenance_with_matrix_label_and_occurrence",
            "nonempty_full_admissible_parameter_domain",
            "verified_error_enclosure_for_every_surviving_parameter",
            "proof_actual_predicted_event_is_inside_its_enclosure",
            "finite_grid_completeness_or_explicitly_limited_scope",
            "validated_units_epoch_reference_frame_holdouts",
            "independent_ground_impact_not_just_altitude_crossing",
        ],
        "conditional_certificates": [
            {
                "code": "CONDE_EXCLUDED",
                "lean": "covered_envelope_excludes_conde",
                "extra": "all covered events disjoint from Conde",
                "impact_elsewhere_implied": False,
            },
            {
                "code": "CONDE_FORCED",
                "lean": "covered_envelope_forces_conde",
                "extra": "every surviving state predicts ground impact and enclosure lies in Conde",
                "impact_elsewhere_implied": False,
            },
            {
                "code": "OTHER_WINDOW",
                "lean": "covered_envelope_identifies_other_window",
                "extra": "all survivors impact in a bounded alternative window disjoint from Conde",
                "impact_elsewhere_implied": True,
            },
        ],
        "source_lineage": [
            {
                "matrix_occurrences": ["C01#1"],
                "chain": "TUPI_FBIS_TRANSCRIPTION_REPORT_ONLY",
                "physical_observation": False,
            },
            {
                "matrix_occurrences": ["C131#1", "C197#1"],
                "chain": "NASA_GODDARD_SSR_1963_11_15_P8",
                "independent_sources": 1,
                "physical_day_admitted": False,
            },
        ],
    }

def unresolved_element_scenarios_interface() -> dict:
    """Sourced orbital baseline with a *free* RAAN parameter for inference.

    The legacy site vector without a traceable TLE is NOT an active scenario.
    Source values are a baseline from ONE secondary catalogue lineage, not
    exact physical constraints. MCMC needs independently justified residual
    uncertainties before any posterior or hard exclusion can be claimed.
    """
    source = {
        "id": "AFSPC_MIRROR_528_1963_10_27",
        "raan_degrees_reported": "198.5261",
        "epoch_utc": "1963-10-27T14:40:16.132512Z",
        "inclination_deg": "81.8615",
        "eccentricity": "0.0017147",
        "arg_perigee_deg": "104.7477",
        "mean_anomaly_deg": "255.4423",
        "mean_motion_rev_day": "15.74901460",
        "source_url": "https://www.itau.magnetic-declination.com/satellite/?s=528",
        "literal_pair_sha256": "18cf11665e061b5ec8679242e10b00b82accf29bc6f0b9b7b6330b9c44e341cd",
        "secondary_numeric_parquet_sha256": "c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09",
        "source_audit_pr": "https://github.com/franklinbaldo/conde-incident/pull/14",
        "matrix_occurrences": ["C25#1", "C179#1"],
        "matrix_citations": [
            f"{SOURCE_REPO}/blob/{MATRIX_COMMIT}/{MATRIX_PATH}#L118",
            f"{SOURCE_REPO}/blob/{MATRIX_COMMIT}/{MATRIX_PATH}#L839",
        ],
        "source_authentication": "NOT_VERIFIED_PRIMARY",
        "reference_only_not_true_raan": True,
        "admitted_as_hard_constraint": False,
    }
    return {
        "version": 2,
        "kind": "SOURCED_REFERENCE_PLUS_INFERRED_ORBITAL_PARAMETERS",
        "lean_module": "Conde1963/ScenarioAlternatives.lean",
        "active_source_lineages": 1,
        "admissible_semantics": "SINGLE_SOURCED_REFERENCE_WITH_FREE_PARAMETERS",
        "branch_combination_allowed": "OTHER_BRANCH_ONLY_IF_NEW_DOCUMENTED_SOURCE",
        "current_scenario": source["id"],
        "chosen_physical_constraints": None,
        "numerically_supported_bounds": None,
        "historical_orbit_validation": "NOT_RUN",
        "original_tle_custody": "NOT_VERIFIED",
        "independent_source_lineages": "NOT_ESTABLISHED",
        "physical_reference_frame_reconciled": False,
        "holdout_529_passed": False,
        "all_branch_error_enclosures_verified": False,
        "alternatives": [source],
        "obsolete_legacy_input": "RETIRED_FROM_ACTIVE_INFERENCE_RETRIEVABLE_FROM_GIT",
        "raan_parameter": {
            "name": "raan_at_reference_epoch_deg",
            "topology": "CIRCLE_MOD_360",
            "full_search_domain_deg": ["0", "360"],
            "upper_endpoint_exclusive": True,
            "reference_value_deg": source["raan_degrees_reported"],
            "reference_epoch_utc": source["epoch_utc"],
            "source_id": source["id"],
            "physical_uncertainty_deg": None,
            "hard_admissible_interval_deg": None,
            "prior_distribution": "UNSPECIFIED_NOT_SYNTHESIZED",
            "inferential_status": "FREE_PARAMETER_UNTIL_JUSTIFIED_CONSTRAINTS",
        },
        "physical_dependencies_to_explore": [
            {
                "relation": "FIRST_ORDER_J2_NODAL_PRECESSION",
                "variables": ["raan_at_reference_epoch_deg", "inclination_deg",
                              "eccentricity", "mean_motion_rev_day", "epoch_utc"],
                "interpretation": "Omega(t)=Omega0+integral(dotOmega_J2)dt modulo 360; physical model approximation",
                "calibrated_error": None,
            },
            {
                "relation": "OBSERVED_RAAN_RESIDUALS_WITH_CIRCULAR_WRAP",
                "variables": ["raan_at_reference_epoch_deg", "other_528_epochs",
                              "reference_frame", "observational_error"],
                "interpretation": "Compare predictions with tracked epochs, preserving source dependence",
                "calibrated_error": None,
            },
            {
                "relation": "CROSS_OBJECT_HOLDOUT_527_529",
                "variables": ["527_epoch_and_elements", "529_epoch_and_elements",
                              "common_dynamics", "independent_holdout"],
                "interpretation": "Validate transferable dynamics, not impose identical RAAN or same orbit",
                "calibrated_error": None,
            },
            {
                "relation": "ATMOSPHERIC_DRAG_AND_SEMI_MAJOR_AXIS",
                "variables": ["density", "cd_area_over_mass", "solar_geomagnetic_inputs",
                              "semi_major_axis", "mean_motion_rev_day"],
                "interpretation": "Fit secular evolution without inventing drag or density measurements",
                "calibrated_error": None,
            },
        ],
        "mcmc_contract": {
            "sampler": "NOT_IMPLEMENTED_BY_LEAN",
            "status": "CONDITIONAL_PARAMETER_EXPLORATION_NOT_POSTERIOR",
            "requires": [
                "identified_epoch_frame_and_literal_source",
                "angular_residuals_of_actual_528_epoch_series",
                "calibrated_observation_and_model_errors_for_likelihood",
                "justified_prior_and_covered_parameter_domain",
                "reproducible_chain_diagnostics_and_predictive_holdouts",
            ],
            "no_empirical_uncertainty_no_posterior_claim": True,
        },
        "required_before_physical_use": [
            "validate_original_element_source_frame_epoch_units_and_checksum",
            "quantify_error_distribution_or_keep_raan_free",
            "derive_raan_restrictions_from_j2_and_multi_epoch_observations",
            "validate_holdout_527_529_with_shared_dynamics_without_trajectory_identity",
            "calibrated_atmospheric_drag_and_nonempty_admissible_domain",
        ],
        "warning": "The only active RAAN baseline is the sourced secondary 528 catalogue record; its error is unknown. The previous unsourced site vector is archived in Git, not a competing observation.",
    }



def scenario_enclosure_interface() -> dict:
    """Proof obligations for calibrated error envelopes across source alternatives.

    NO real trajectory, calibrated interval or terminal observation is asserted.
    The two alternative RAAN claims are neither independently authenticated
    nor safely intersectable. NASA C131/C197 share one documentary lineage.
    """
    scenarios = unresolved_element_scenarios_interface()
    return {
        "version": 1,
        "kind": "CONDITIONAL_DISJUNCTIVE_ENCLOSURES_NOT_HISTORICAL_PREDICTIONS",
        "lean_module": "Conde1963/ScenarioEnclosures.lean",
        "candidate_semantics": "COMMON_AND_LEFT_OR_RIGHT",
        "branch_combination": "UNION_UNTIL_VERIFIED_SOURCE_ADJUDICATION",
        "source_branches": [
            {
                "id": branch["id"],
                "original_custody": branch["source_authentication"],
                "matrix_occurrences": branch["matrix_occurrences"],
                "is_hard_physical_constraint": False,
            } for branch in scenarios["alternatives"]
        ],
        "nasa_lineage": {
            "matrix_occurrences": ["C131#1", "C197#1"],
            "source_count": 1,
            "instrumental_trajectory_measurements": 0,
            "physical_decay_time_or_location_established": False,
        },
        "source_matrix_sha1": MATRIX_SHA1,
        "current_geographic_verdict": None,
        "predicted_ground_impact": None,
        "validated_error_enclosures": None,
        "global_parameter_domain_certified": False,
        "source_branch_authenticity_certified": False,
        "independent_529_holdout_passed": False,
        "ground_impact_gate_verified": False,
        "historical_zip_154_propositions_151_labels": "NOT_RUN",
        "lean_obligations": {
            "exclusion": "covered_alternative_envelope_excludes_conde",
            "forcing": "covered_alternative_envelope_forces_conde",
            "other_window": "covered_alternative_envelope_identifies_other_window",
            "consistent_refinement_exclusion": "alternative_enclosure_exclusion_persists_with_witness",
            "consistent_refinement_forcing": "alternative_enclosure_forcing_persists_with_witness",
            "consistent_refinement_other": "alternative_enclosure_other_window_persists_with_witness",
            "one_branch_only_if_other_empty": "proven_empty_right_branch_allows_left_exclusion",
            "opposed_branch_witnesses": "opposing_branch_witnesses_block_gated_verdicts",
            "missing_gate_blocks_all": "missing_ground_audit_blocks_all_alternative_verdicts",
        },
        "mandatory_checks": [
            "source_row_identity_and_occurrence_in_pinned_matrix",
            "instrumental_lineage_frame_epoch_units_and_checksum",
            "do_not_intersect_incompatible_source_branches",
            "nonempty_global_domain_and_proven_strict_reduction",
            "sound_numerical_event_enclosure_for_every_survivor_in_each_branch",
            "calibrated_coupled_model_with_error_holdouts_including_529",
            "validated_ground_impact_not_just_altitude_threshold",
            "geographic_disjointness_with_numerical_error_enclosure",
            "one_branch_only_if_other_is_proven_empty",
            "no_geographic_claim_while_surviving_branches_disagree",
        ],
    }


def finite_coverage_interface() -> dict:
    """Typed proof obligations for finite grids, NOT a global orbit survey.

    A correct pointwise classifier does not show exhaustive physical-domain
    coverage. An empty grid has no evidential effect without such coverage.
    """
    return {
        "version": 1,
        "kind": "GLOBAL_COVERAGE_REQUIRED_BEFORE_EMPTY_GRID_EXCLUDES_BRANCH",
        "lean_module": "Conde1963/FiniteCoverage.lean",
        "source_matrix_sha1": MATRIX_SHA1,
        "parameter_semantics": "COMMON_AND_LEFT_OR_RIGHT",
        "source_matrix_occurrences": ["C25#1", "C179#1"],
        "nasa_same_primary_source": ["C131#1", "C197#1"],
        "nasa_independent_source_count": 1,
        "original_zip_154_151_import": "NOT_RUN",
        "current_screen": None,
        "current_global_domain_conclusion": None,
        "current_geographic_verdict": None,
        "verified_numeric_enclosures": None,
        "pointwise_classifier_equivalence_proven": False,
        "full_domain_coverage_proven": False,
        "primary_tle_custody_proven": False,
        "independent_529_holdout_passed": False,
        "ground_impact_gate_proven": False,
        "lean_obligations": {
            "pointwise_iff": "passing_iff_sampled_admissible",
            "surviving_witness": "passing_witness_proves_global_nonempty",
            "no_fabrication": "passing_never_creates_parameter",
            "empty_only_with_coverage": "empty_passing_implies_empty_domain_with_coverage",
            "branch_elimination": "exhaustive_empty_right_screen_eliminates_right_branch",
            "left_result_only_after_branch_elimination": "exhaustive_right_screen_licenses_left_exclusion",
            "sampled_empty_counterexample": "empty_sample_does_not_eliminate_unseen_branch",
        },
        "must_verify": [
            "explicit_source_scenario_and_matrix_occurrence",
            "pointwise_screen_equivalence_for_each_sample",
            "proof_every_global_admissible_state_is_covered",
            "nonempty_remaining_branch_with_error_bounded_ground_impact_model",
            "no_independent_source_inference_from_duplicate_NASA_citations",
            "no_physical_claim_from_synthetic_countermodel",
        ],
    }



def certified_cell_interface() -> dict:
    """Finite cells may cover a continuous domain, unlike sampled points.

    The Lean theorems are conditional on a proof of coverage and sound
    event bounds for *every* surviving physical parameter in the union of
    unresolved source scenarios. No actual cell decomposition is supplied.
    """
    return {
        "version": 1,
        "kind": "CONTINUOUS_PARAMETER_CELL_COVER_NOT_POINT_GRID",
        "lean_module": "Conde1963/CertifiedCells.lean",
        "source_matrix_sha1": MATRIX_SHA1,
        "parameter_semantics": "COMMON_AND_LEFT_OR_RIGHT",
        "orbital_scenario_rows": ["C25#1", "C179#1"],
        "orbital_primary_tle_status": "NOT_AUTHENTICATED",
        "nasa_one_document_two_occurrences": ["C131#1", "C197#1"],
        "nasa_independent_instrumental_sources": 0,
        "original_zip_154_151_import": "NOT_RUN",
        "current_cells": None,
        "current_event_bounds": None,
        "current_geographic_verdict": None,
        "current_numeric_epoch_window_utc": None,
        "current_numeric_spatial_enclosure": None,
        "continuous_parameter_coverage_proven": False,
        "sound_event_bounds_for_every_cell_proven": False,
        "nonempty_global_domain_proven": False,
        "validated_ground_impact_gate_proven": False,
        "calibrated_numerical_errors_proven": False,
        "independent_529_holdout_passed": False,
        "lean_obligations": {
            "event_soundness": "predicted_event_has_certified_cell_bound",
            "nonempty_requires_cell": "nonempty_domain_requires_listed_cell",
            "empty_cells_requires_full_cover": "empty_certified_cells_imply_empty_domain",
            "exclude_conditional": "covered_cells_exclude_conde",
            "force_conditional": "covered_cells_force_conde",
            "other_window_conditional": "covered_cells_identify_other_window",
            "narrowed_cover": "cell_cover_survives_common_narrowing",
            "narrowed_event_bounds": "cell_bounds_survive_common_narrowing",
        },
        "must_verify": [
            "authentic_primary_tle_epochs_and_coordinate_frames",
            "independent_proof_all_admissible_parameters_lie_in_listed_cells",
            "sound_numerical_event_bounds_for_all_parameters_in_each_cell",
            "nonempty_surviving_domain_after_each_narrowing",
            "independent_holdout_529_and_quantified_integrator_error",
            "ground_impact_model_not_just_catalogue_decay_or_altitude_crossing",
            "all_surviving_RAAN_scenarios_in_union_not_intersection",
            "other_window_disjoint_from_conde_with_error_bounds",
        ],
    }



def paired_certified_enclosure_interface() -> dict:
    """Conditional intersection of two sound cell enclosures for one model.

    Two declared enclosures do not imply independent source observations;
    every cell cover, numerical soundness certificate and input custody
    must be independently established before any physical inference.
    """
    return {
        "version": 1,
        "kind": "PAIRED_SOUND_CELL_EVENT_INTERSECTION",
        "lean_module": "Conde1963/PairedEnclosures.lean",
        "source_matrix_sha1": MATRIX_SHA1,
        "parameter_semantics": "COMMON_AND_LEFT_OR_RIGHT",
        "unresolved_orbital_occurrences": ["C25#1", "C179#1"],
        "same_nasa_document_occurrences": ["C131#1", "C197#1"],
        "nasa_independent_instrumental_sources": 0,
        "original_zip_154_151_import": "NOT_RUN",
        "current_first_cover": None,
        "current_second_cover": None,
        "current_intersection": None,
        "current_geographic_verdict": None,
        "current_numeric_impact_window": None,
        "primary_tle_custody_verified": False,
        "both_continuous_domain_covers_verified": False,
        "both_event_enclosures_proved_sound": False,
        "same_physical_predictor_and_reference_frame_verified": False,
        "nonempty_admissible_domain_proven": False,
        "universal_ground_impact_predicted": False,
        "calibrated_error_and_holdout_529_verified": False,
        "ground_impact_audit_passed": False,
        "lean_obligations": {
            "common_prediction_soundness": "paired_certified_bounds_for_prediction",
            "conditional_conde_excluded": "paired_enclosures_exclude_conde",
            "conditional_conde_forced": "paired_enclosures_force_conde",
            "conditional_other_window": "paired_enclosures_identify_other_window",
            "disjoint_bounds_no_predicted_impact": "disjoint_paired_bounds_forbid_predicted_impact",
            "incompatible_bounds_vs_universal_impact": "incompatible_paired_bounds_refute_universal_impact",
            "narrowing_preserves_soundness": "paired_bounds_survive_common_narrowing",
        },
        "must_verify": [
            "source_matrix_occurrence_identity_and_nonindependence",
            "verified_primary_TLE_epoch_frame_units_and_provenance",
            "global_parameter_cover_for_each_cell_family_not_grid_only",
            "both_event_bounds_sound_for_every_surviving_candidate",
            "both_covers_refer_to_exact_same_model_and_parameter_domain",
            "intersection_error_propagation_and_model_calibration",
            "nonempty_surviving_domain_after_each_narrowing",
            "independent_physical_holdout_529",
            "ground_impact_vs_altitude_crossing_and_material_survival",
            "geographic_disjointness_with_validated_error",
            "do_not_infer_measurement_independence_from_two_certificates",
            "no_geographic_verdict_until_empirical_gates_pass",
        ],
    }



def truth_bridge_interface() -> dict:
    """Physical event truth is NOT implied by model self-soundness.

    Nothing here asserts that a real ground impact occurred, nor even
    that a sound bridge to hypothetical true events has been established.
    The separate TruthLink.actualCovered premise is uninstantiated.
    """
    return {
        "version": 1,
        "kind": "EXTERNAL_TRUTH_LINK_REQUIRED_NOT_SIMULATOR_SELF_SOUNDED",
        "lean_module": "Conde1963/TruthBridge.lean",
        "source_matrix_sha1": MATRIX_SHA1,
        "source_matrix_commit": MATRIX_COMMIT,
        "unverified_orbital_element_occurrences": ["C25#1", "C179#1"],
        "reported_incident_occurrence": "C01#1",
        "single_nasa_document_occurrences": ["C131#1", "C197#1"],
        "nasa_documentary_lineage_count": 1,
        "nasa_independent_terminal_measurements": 0,
        "source_scenarios": "UNRESOLVED_OR_UNION_NOT_INTERSECTION",
        "historical_zip_154_151": "NOT_RUN",
        "forecast_output": None,
        "hypothetical_actual_ground_impact": None,
        "physical_time_window": None,
        "physical_geographic_region": None,
        "truth_link_proof": None,
        "primary_tle_custody_verified": False,
        "independent_physical_holdout_529_passed": False,
        "numerical_error_enclosure_verified": False,
        "full_continuous_domain_cover_verified": False,
        "ground_impact_and_material_survival_verified": False,
        "simulator_prediction_soundness_proves_physical_truth": False,
        "current_physical_outcome": None,
        "lean_obligations": {
            "actual_event_cover": "hypothetical_actual_event_has_certified_cell_bound",
            "conditional_actual_exclusion": "certified_truth_excludes_conde",
            "conditional_actual_forcing": "certified_truth_forces_conde",
            "conditional_other_window": "certified_truth_identifies_other_window",
            "nonempty_refinement": "certified_truth_exclusion_persists_with_witness",
            "nonimpact_counterexample": "absent_actual_impact_refutes_truth_forcing",
            "self_soundness_counterexample": "self_sound_forecast_does_not_cover_unlinked_reality",
        },
        "must_verify": [
            "matrix_occurrence_and_documentary_lineage_are_exact",
            "historical_input_TLE_source_custody_epoch_frame_units",
            "source_alternatives_are_union_until_independent_adjudication",
            "all_surviving_parameters_have_sound_continuous_cell_cover",
            "predicted_event_enclosure_does_not_certify_actual_event",
            "external_truth_link_for_every_admissible_physical_state",
            "independent_529_holdout_and_calibrated_numerical_error",
            "ground_contact_and_material_survival_not_altitude_threshold",
            "nonempty_surviving_domain_with_universal_ground_impact_for_forcing",
            "separate_proof_of_geographic_window_disjointness",
            "no_physical_verdict_until_every_external_gate_is_justified",
        ],
    }


def contracts(rows: list[dict]) -> dict:
    return {
        "schema_version": 2,
        "kind": "DOCUMENTARY_TRACEABILITY_NOT_PHYSICAL_TRAJECTORIES",
        "matrix_git_blob_sha1": MATRIX_SHA1,
        "matrix_commit": MATRIX_COMMIT,
        "original_lean_zip_status": "NOT_RUN",
        "outcome_interface": outcome_interface(),
        "enclosure_interface": enclosure_interface(),
        "unresolved_element_scenarios_interface": unresolved_element_scenarios_interface(),
        "scenario_enclosure_interface": scenario_enclosure_interface(),
        "finite_coverage_interface": finite_coverage_interface(),
        "certified_cell_interface": certified_cell_interface(),
        "paired_certified_enclosure_interface": paired_certified_enclosure_interface(),
        "truth_bridge_interface": truth_bridge_interface(),
        "scope": "241 actual rows, 238 distinct labels, no fabricated observations",
        "entries": [
            {
                "id": f'C{r["number"]:02d}',
                "occurrence": r["occurrence"],
                "line": r["line"],
                "citation": f'{SOURCE_REPO}/blob/{MATRIX_COMMIT}/{MATRIX_PATH}#L{r["line"]}',
                "source_status": "MATRIX_ONLY_NOT_REINSPECTED_THIS_RUN",
                "epistemic_uncertainty": r["uncertainty"],
                "uncertainty_basis": (
                    "Historical text says a claim was broadcast; physical occurrence unverified."
                    if r["uncertainty"] == "reportExistsPhysicalOccurrenceUnverified"
                    else "NASA publication records a decay date; actual physical decay date, timing, and method unknown."
                    if r["uncertainty"] == "reportedCatalogueDayActualDayUnknown"
                    else "Row-level uncertainty not yet individually assessed in Lean transfer; preserve source matrix's own qualifiers."
                ),
                "numeric_error_bounds": None,
                "ground_impact_verification": "NOT_ESTABLISHED",
                "section": r["section"],
                "row_markdown": r["row_markdown"],
                "physical_encoding": (
                    "NASA_CATALOGUED_DATE_HYPOTHESIS_NOT_HARD_FILTER"
                    if r["role"] == "nasaReportedDecayDay"
                    else "NOT_ADMITTED_AS_TERMINAL_STATE_CONSTRAINT"
                ),
                "source_chain": (
                    "NASA_GODDARD_SSR_1963_11_15_P8"
                    if r["role"] == "nasaReportedDecayDay" else None
                ),
            }
            for r in rows
        ],
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--matrix", type=Path, default=Path(MATRIX_PATH))
    p.add_argument("--check", type=Path, help="compare complete generated Lean registry")
    p.add_argument("--json", type=Path, help="write JSON contract for Castor, not model data")
    args = p.parse_args()
    try:
        data = args.matrix.read_bytes()
        rows = parse_rows(data)
        report = audit(data, rows)
        generated = render_lean(rows)
        if args.check:
            if args.check.read_text(encoding="utf-8") != generated:
                raise InventoryError("Lean registry is stale or entries were changed")
        if args.json:
            args.json.write_text(json.dumps(
                contracts(rows), ensure_ascii=False, indent=2
            ) + "\n", encoding="utf-8")
    except (OSError, InventoryError) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}))
        return 1
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
