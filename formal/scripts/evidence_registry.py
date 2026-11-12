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
                "chain": "TUPI_F BIS_TRANSCRIPTION_REPORT_ONLY".replace(" ", ""),
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

def contracts(rows: list[dict]) -> dict:
    return {
        "schema_version": 2,
        "kind": "DOCUMENTARY_TRACEABILITY_NOT_PHYSICAL_TRAJECTORIES",
        "matrix_git_blob_sha1": MATRIX_SHA1,
        "matrix_commit": MATRIX_COMMIT,
        "original_lean_zip_status": "NOT_RUN",
        "outcome_interface": outcome_interface(),
        "enclosure_interface": enclosure_interface(),
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
