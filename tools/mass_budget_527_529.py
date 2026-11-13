#!/usr/bin/env python3
"""C241 mass-budget scenario: 527 + 528 + 529 + X = 1176 kg + epsilon.

This is conditional conservation from a secondary approximate catalogue value.
No untracked-mass bound, catalog error bound, physical area or Cd is observed.
"""
import argparse
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "research/constraints/C241_mass_budget_residual_2026-11-13.json"
MATRIX = ROOT / "research/evidence_matrix_C001-C238_2026-11-11.md"
IDENTITY = ROOT / "research/tle_custody/gcat_full_catalog_lineage_C241-L14.json"
BASE = Decimal("1176")


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def validate(model: dict, matrix: str, identity: dict) -> None:
    require(model.get("schema") == "conde.mass-budget-527-529-residual/v1"
            and model.get("id") == "C241-MASS-X-20261113"
            and model.get("status") == "CONNECTED_CONDITIONAL_NOT_HISTORICAL_BOUND",
            "mass model identity")
    rows = [line for line in matrix.splitlines() if line.startswith("| C61 |")]
    require(len(rows) == 1, "C61 source occurrence must be unique")
    require("~1176 kg" in rows[0] and "~306 kg" in rows[0]
            and "528/529" in rows[0] and "placeholders desconhecidos" in rows[0],
            "source C61 row changed")
    src = model["source"]
    require(src["matrix_occurrence"] == "C61"
            and src["matrix_path"] == "research/evidence_matrix_C001-C238_2026-11-11.md"
            and src["catalog_url"] == "https://planet4589.org/space/gcat/data/cat/satcat.html"
            and src["associated_total_mass_kg_approx"] == 1176
            and src["other_c61_quantity_dry_mass_kg_approx"] == 306
            and src["mass_type"] ==
              "ASSOCIATED_TOTAL_MASS_APPROXIMATE_NOT_AUTHENTICATED_THREE_PARTITION_INVENTORY"
            and src["observed_individual_mass_of_528_kg"] is None
            and src["reference_mass_epoch_utc"] is None
            and not src["claim_that_1176_is_closed_orbital_mass_for_three"]
            and not src["catalog_family_is_independent_engineering_measurement"],
            "catalog provenance promoted")
    require(src["satellite_crosswalk"] == identity["record_id"] == "C241-L14"
            and [identity["catalogue_labels"][f"00527"]['cospar'],
                 identity["catalogue_labels"][f"00528"]['cospar'],
                 identity["catalogue_labels"][f"00529"]['cospar']] ==
                 ["1963-003A","1963-003B","1963-003C"]
            and identity["comparisons"]["independent_tracking_sources"] == 0,
            "identity changed")
    v = model["variables"]
    require([x["id"] for x in v] ==
            ["mass_527","mass_528","mass_529","X_untracked","epsilon_reference"],
            "object-specific mass variables changed")
    require(all(x["unit"] == "kg" for x in v)
            and v[3]["value"] is None and not v[3]["automatically_small"]
            and v[4]["value"] is None and v[4]["numeric_error_bound"] is None,
            "unknown mass/error fabricated")
    require("expended propellant if included in starting mass" in v[3]["may_include"],
            "X reference accounting ambiguity lost")
    b = model["conditional_budget"]
    require(b["equation"] ==
            "m_527 + m_528 + m_529 + X_untracked = 1176 kg + epsilon_reference"
            and b["positive_individual_masses_assumed"]
            and b["untracked_nonnegative_assumed"]
            and b["epsilon_numeric_distribution"] is None
            and b["mass_accounting_epoch_utc"] is None
            and not b["closed_three_body_equation_activated"]
            and not b["physically_calibrated_historical_constraint"]
            and not b["mass_reference_convention_verified"],
            "unverified exact three-body mass constraint activated")
    derived = model["conditional_derived_bounds"]
    require(derived["E_kg"] is None and derived["R_kg"] is None
            and all(derived[k] is None for k in
              ("bound_on_individual_area_m2", "bound_on_individual_diameter_m",
               "bound_on_individual_Cd_A_over_m"))
            and not derived["numeric_historical_domain_reduction"],
            "false calibrated mass/area bounds")
    require(model["drag_bridge"]["shared_atmosphere_scale_unidentified"]
            and not model["drag_bridge"]["direct_identification_of_masses_from_effective_k"],
            "drag gauge falsely resolved")
    require(len(model["graph_edges"]) == 6
            and not model["historical_mass_of_any_object_estimated"]
            and model["conde_impact_inference"] == "NOT_SUPPORTED",
            "premature physical inference")


def optional_nonnegative(value):
    if value is None:
        return None
    try:
        result = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError("invalid numeric scenario parameter") from exc
    require(result.is_finite() and result >= 0, "scenario bounds must be nonnegative finite")
    return result


def scenario(model, error_max_kg=None, x_max_kg=None) -> dict:
    E = optional_nonnegative(error_max_kg)
    R = optional_nonnegative(x_max_kg)
    if E is None:
        return {
            "status": "UNBOUNDED_BY_GIVEN_CATALOG_ERROR",
            "E_kg": None, "R_kg": str(R) if R is not None else None,
            "tracked_mass_sum_min_infimum_kg": None,
            "tracked_mass_sum_max_kg": None,
            "individual_mass_upper_exclusive_kg": None,
            "physical_constraint_active": False,
            "historical_certainty": "NOT_ESTABLISHED",
            "note": "The quoted ~1176 kg is not a certified closed inventory; unknown epsilon prevents a numeric upper bound.",
        }
    bottom = max(Decimal("0"), BASE - E - (R if R is not None else BASE + E))
    top = BASE + E
    return {
        "status": "CONDITIONAL_SCENARIO_ONLY",
        "E_kg": str(E), "R_kg": str(R) if R is not None else None,
        "tracked_mass_sum_min_infimum_kg": str(bottom),
        "tracked_mass_sum_max_kg": str(top),
        "individual_mass_upper_exclusive_kg": str(top),
        "positive_individual_masses": True,
        "physical_constraint_active": False,
        "historical_certainty": "NOT_ESTABLISHED",
        "note": "E and R are user-supplied assumptions, not measured NASA/GCAT errors or untracked fractions.",
    }


def report(model, matrix, identity, *, error_max_kg=None, x_max_kg=None):
    validate(model, matrix, identity)
    return {
        "id": model["id"],
        "source_occurrence": "C61",
        "catalog_approximate_mass_kg": 1176,
        "model": model["conditional_budget"]["equation"],
        "unknown_X_may_be_large": True,
        "reference_mass_accuracy_known": False,
        "residual_mass_bound_observed": False,
        "scenario": scenario(model, error_max_kg, x_max_kg),
        "historical_domain_reduction": False,
        "individual_area_or_shape_inferred": False,
        "conde": "INDETERMINATE",
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--error-max-kg", type=str, default=None)
    p.add_argument("--untracked-max-kg", type=str, default=None)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    model = json.loads(MODEL.read_text(encoding="utf-8"))
    identity = json.loads(IDENTITY.read_text(encoding="utf-8"))
    result = report(model, MATRIX.read_text(encoding="utf-8"), identity,
                    error_max_kg=args.error_max_kg,
                    x_max_kg=args.untracked_max_kg)
    payload = json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")


if __name__ == "__main__":
    main()
