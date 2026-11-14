#!/usr/bin/env python3
"""C241: exact mass identifiability audit; not a historical posterior."""
import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GCAT = ROOT / "research/tle_custody/gcat_mass_semantics_C241-L40.json"
OBJECTS = ("527", "528", "529", "X")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def catalog_is_not_mass_inventory(data):
    """Fail closed if the original GCAT field-semantics audit changes."""
    rows = data["rows"]
    conclusion = data["conclusion"]
    require(data["id"] == "C241-L40"
            and rows["S00527"]["mass_kg"] == 306
            and rows["S00527"]["total_mass_kg"] == 1176
            and rows["A00324"]["mass_kg"] == 900
            and rows["A00324"]["dry_mass_kg"] == 870
            and all(rows[k]["mass_catalog_value_kg"] == 0
                    and rows[k]["mass_kg"] is None
                    for k in ("S00528", "S00529"))
            and data["derived_checks"]["three_norad_objects_mass_sum_kg"] is None
            and conclusion["it_is_not_a_documented_sum_of_exclusive_527_528_529"]
            and conclusion["zero_for_debris_is_not_physical_mass_zero"]
            and not conclusion["parent_launch_mass_balance_proven"]
            and not conclusion["historical_mass_constraint_active"],
            "GCAT provenance must not become a measured 527+528+529 inventory")
    return True


def rank(rows, columns=4):
    """Exact rational row rank, without an arbitrary SVD tolerance."""
    matrix = [[Fraction(x) for x in row] for row in rows]
    require(all(len(row) == columns for row in matrix), "wrong matrix dimension")
    i = 0
    for j in range(columns):
        pivot = next((k for k in range(i, len(matrix)) if matrix[k][j]), None)
        if pivot is None:
            continue
        matrix[i], matrix[pivot] = matrix[pivot], matrix[i]
        den = matrix[i][j]
        matrix[i] = [x / den for x in matrix[i]]
        for k in range(len(matrix)):
            if k == i:
                continue
            c = matrix[k][j]
            matrix[k] = [a - c * b for a, b in zip(matrix[k], matrix[i])]
        i += 1
        if i == len(matrix):
            break
    return i


def scenario_rows(*, inventory_assumed=False, independent_mass_objects=()):
    """Only hypothetical design: these rows are NOT historical evidence."""
    require(len(set(independent_mass_objects)) == len(independent_mass_objects)
            and all(x in OBJECTS for x in independent_mass_objects),
            "measurement labels must be distinct known components")
    rows = [[1, 1, 1, 1]] if inventory_assumed else []
    for name in independent_mass_objects:
        rows.append([int(name == obj) for obj in OBJECTS])
    return rows


def exact_drag_counterexample(masses, cd_areas, transfer):
    """Preserve hypothetical total and each B=CdA/m, with masses nonunique."""
    require(len(masses) == 4 and len(cd_areas) == 3,
            "need 527, 528, 529, X and three CdA products")
    m = tuple(Fraction(x) for x in masses)
    a = tuple(Fraction(x) for x in cd_areas)
    d = Fraction(transfer)
    require(all(x > 0 for x in m[:3]) and m[3] >= 0
            and all(x > 0 for x in a) and d != 0,
            "positive physical parameters and nonzero transfer required")
    moved = (m[0] + d, m[1] - d, m[2], m[3])
    require(all(x > 0 for x in moved[:3]), "transfer violates positivity")
    new_areas = (a[0] * moved[0] / m[0],
                 a[1] * moved[1] / m[1], a[2])
    old_drag = tuple(a[j] / m[j] for j in range(3))
    new_drag = tuple(new_areas[j] / moved[j] for j in range(3))
    require(sum(m) == sum(moved) and old_drag == new_drag,
            "counterexample failed conservation")
    return {"different_mass_partitions": m != moved,
            "total_preserved": True, "all_three_B_preserved": True}


def audit():
    original = GCAT.read_bytes()
    source = json.loads(original)
    catalog_is_not_mass_inventory(source)
    historical = rank([])
    conditional = rank(scenario_rows(inventory_assumed=True))
    two_mass = rank(scenario_rows(inventory_assumed=True,
                                  independent_mass_objects=("528", "529")))
    three_mass = rank(scenario_rows(inventory_assumed=True,
                                    independent_mass_objects=("527", "528", "529")))
    witness = exact_drag_counterexample(
        (500, 200, 100, 376), (10, 5, 2), 50)
    return {
        "id": "C241-CERVO-MASS-RANK-R11",
        "source_occurrence": "C241-L40",
        "source_sha256": hashlib.sha256(original).hexdigest(),
        "source_url": "https://planet4589.org/space/gcat/web/cat/cols.html",
        "physical_parameters": list(OBJECTS),
        "historical_mass_observation_rank": historical,
        "historical_mass_nullity": 4 - historical,
        "scenario_only_total_rank": conditional,
        "scenario_only_total_nullity": 4 - conditional,
        "scenario_total_plus_two_masses_rank": two_mass,
        "scenario_total_plus_three_masses_rank": three_mass,
        "counterexample": witness,
        "scenario_mass_total_is_historically_validated": False,
        "source_family_independent_mass_measurements": 0,
        "instrumental_528_observations_added": 0,
        "historical_mcmc": "NOT_RUN",
        "historical_mass_posterior": None,
        "physical_domain_reduction": False,
        "limitations": ("The ranks describe the four mass coordinates only. "
                        "Even a valid total inventory needs a common epoch, "
                        "crosswalk, bounded losses and independently calibrated "
                        "component measurements. Unknown CdA and atmosphere "
                        "cannot be converted into mass measurements.")
    }


def main():
    print(json.dumps(audit(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
