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
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["schema"] == "conde.mass-partition-proposal/v1"
    assert data["object_ids"] == [527, 528, 529]
    assert data["nominal_total_kg"] == 1176
    assert data["epistemic_grade"] == "USER_HYPOTHESIS_UNVERIFIED"
    for key in ("primary_publication", "source_page", "source_sha256", "reference_epoch_utc", "mass_definition"):
        assert data["source"][key] is None
    assert data["source"]["object_coverage_confirmed"] is False
    assert data["unknowns_kg"] == {k: None for k in (*KEYS, "delta_total_measurement")}
    for key in ("epsilon_total_kg", "x_independently_bounded_kg"):
        assert data["assumptions"][key] is None
    for key in ("x_is_small", "full_partition_of_total"):
        assert data["assumptions"][key] == "NOT_ESTABLISHED"
    for guard in ("physical_constraint_active", "used_to_fit_drag", "used_for_lean_historical_facts"):
        assert data["activation"][guard] is False


if __name__ == "__main__":
    audit_ledger()
    print("C241-L39: PASS (conditional model, physical activation false)")
