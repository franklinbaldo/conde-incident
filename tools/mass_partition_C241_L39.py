"""Conservative exact arithmetic for the conditional 527/528/529 mass budget."""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
from pathlib import Path
import json

LEDGER = Path(__file__).resolve().parents[1] / "research/tle_custody/mass_partition_C241-L39.json"
KEYS = ("m_527", "m_528", "m_529", "x_unaccounted")


def nonnegative(value: object) -> Decimal:
    if isinstance(value, bool) or value is None:
        raise ValueError("Finite nonnegative mass required")
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError("Invalid mass") from exc
    if not number.is_finite() or number < 0:
        raise ValueError("Mass must be finite and nonnegative")
    return number


def check_candidate(masses: dict[str, object], *, total: object = 1176,
                    epsilon: object = 0) -> bool:
    """Check only a hypothetical allocation, never an observed satellite mass."""
    if set(masses) != set(KEYS):
        raise ValueError("Exactly the three masses and residual x are required")
    t, e = nonnegative(total), nonnegative(epsilon)
    computed_sum = sum((nonnegative(masses[k]) for k in KEYS), Decimal(0))
    return abs(computed_sum - t) <= e


def audit_ledger(path: Path = LEDGER) -> None:
    """Validate historical-activation invariants even under python -O.

    The v1 ledger is a frozen *hypothesis*, not an observation. Unknown fields
    and altered epistemic flags must fail closed instead of being forwarded to
    downstream models as measurements.
    """
    def unique_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"C241-L39: duplicate JSON key {key}")
            result[key] = value
        return result

    data = json.loads(path.read_text(encoding="utf-8"),
                      object_pairs_hook=unique_keys)
    if not isinstance(data, dict) or set(data) != {
        "schema", "id", "subject", "epistemic_grade", "source", "object_ids",
        "nominal_total_kg", "unknowns_kg", "assumptions", "equation", "scope",
        "activation", "links",
    }:
        raise ValueError("C241-L39: invalid ledger schema")

    expected = {
        "schema": "conde.mass-partition-proposal/v1",
        "id": "C241-L39",
        "subject": "1963-003A/B/C | NORAD 527/528/529",
        "epistemic_grade": "USER_HYPOTHESIS_UNVERIFIED",
        "source": {
            "statement": "1176 kg is the combined mass of all three objects, with possible untracked or earlier-lost material",
            "origin": "proprietor discussion, 2026-11-13",
            "primary_publication": None,
            "source_page": None,
            "source_sha256": None,
            "reference_epoch_utc": None,
            "mass_definition": None,
            "object_coverage_confirmed": False,
        },
        "object_ids": [527, 528, 529],
        "nominal_total_kg": 1176,
        "unknowns_kg": {key: None for key in (*KEYS, "delta_total_measurement")},
        "assumptions": {
            "masses_nonnegative": True,
            "x_nonnegative": True,
            "same_reference_epoch_required": True,
            "epsilon_total_kg": None,
            "x_independently_bounded_kg": None,
            "x_is_small": "NOT_ESTABLISHED",
            "full_partition_of_total": "NOT_ESTABLISHED",
        },
        "equation": "m_527 + m_528 + m_529 + x_unaccounted = 1176 + delta_total_measurement (kg)",
        "scope": "CONDITIONAL_MASS_BUDGET_NOT_AN_ORBITAL_OBSERVATION",
        "activation": {
            "physical_constraint_active": False,
            "used_to_fit_drag": False,
            "used_for_lean_historical_facts": False,
            "reason": "No primary mass source, definition, common epoch, or tolerance has been verified",
        },
        "links": {
            "catalog_identity": "C241-L32",
            "orbital_fits": "C241-P1",
            "effective_drag_exploration": "Conde PR #619",
            "independent_mass_provenance": "PENDING",
        },
    }
    # Equality alone accepts 1176.0 == 1176 and True == 1. Reject those types.
    if type(data["nominal_total_kg"]) is not int or data != expected:
        raise ValueError("C241-L39: unverified source, allocation or physical activation")

if __name__ == "__main__":
    audit_ledger()
    print("C241-L39: PASS (conditional model, physical activation false)")
