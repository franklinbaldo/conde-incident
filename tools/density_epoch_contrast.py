#!/usr/bin/env python3
"""C241-P29: exact, conditional two-object/two-epoch density-shape design.

No historical acceleration, tracking likelihood, or posterior is computed.
"""
import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "research/constraints/baker_nunn_ru301_1963_film_index.json"
OUTPUT = ROOT / "research/constraints/C241-P29_density_epoch_contrast.json"
# Four SYNTHETIC cells (NORAD IDs are design labels, not observations).
CELLS = ((527, 0, 480), (529, 0, 520), (527, 1, 500), (529, 1, 510))
H0_KM = 500
WEIGHTS = (-1, 1, 1, -1)


def rank_exact(rows):
    """Gaussian elimination over rationals: no arbitrary SVD tolerance."""
    if not rows:
        return 0
    a = [[Fraction(x) for x in row] for row in rows]
    width = len(a[0])
    if any(len(row) != width for row in a):
        raise ValueError("ragged design")
    r = 0
    for col in range(width):
        pivot = next((i for i in range(r, len(a)) if a[i][col]), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        scale = a[r][col]
        a[r] = [x / scale for x in a[r]]
        for i in range(len(a)):
            if i == r:
                continue
            factor = a[i][col]
            if factor:
                a[i] = [x - factor * y for x, y in zip(a[i], a[r])]
        r += 1
        if r == len(a):
            break
    return r


def design(cells=CELLS, *, per_object_epoch_q=False, include_528=False):
    """Columns: log A, two log B, time-varying log q, gamma=1/H."""
    rows = []
    for object_id, epoch, height in cells:
        common = [1, int(object_id == 527), int(object_id == 529)]
        if include_528:
            common += [int(object_id == 528)]
        if per_object_epoch_q:
            common += [
                int((object_id, epoch) == k)
                for k in ((527, 0), (529, 0), (527, 1), (529, 1))
            ]
        else:
            common += [int(epoch == 0), int(epoch == 1)]
        rows.append(common + [-(height - H0_KM)])
    return rows


def archive_snapshot():
    raw = SOURCE.read_bytes()
    doc = json.loads(raw)
    films = doc["film_index_entries"]
    if len({x["id"] for x in films}) != len(films):
        raise ValueError("duplicate film IDs")
    attributable = [x for x in films if x["object_catalog_id"] == 528]
    # Archival index is not an angular observation or a non-detection log.
    ready = [
        x for x in films
        if x.get("object_catalog_id") == 528
        and x.get("observation_epoch_utc") is not None
        and x.get("angular_values") is not None
        and x.get("angular_uncertainty") is not None
        and x.get("frame") is not None
        and x.get("film_sheet_content_inspected") is True
    ]
    if any(x.get("hard_physical_constraint") is True for x in films):
        raise ValueError("archival film locator promoted to hard physical constraint")
    return {
        "source_path": SOURCE.relative_to(ROOT).as_posix(),
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "archival_film_locators": len(films),
        "locators_explicitly_attributed_to_528": len(attributable),
        "candidate_calibrated_528_records": len(ready),
        "caution": "Index-only inventory is neither complete tracking log nor negative detection.",
    }


def build_report():
    full = design()
    nuisance = [row[:-1] for row in full]
    per_object = design(per_object_epoch_q=True)
    no_interaction = design(((527, 0, 480), (529, 0, 520),
                             (527, 1, 500), (529, 1, 540)))
    delta_h = (CELLS[2][2] - CELLS[3][2]) - (CELLS[0][2] - CELLS[1][2])
    contrast = [sum(w * row[col] for w, row in zip(WEIGHTS, full))
                for col in range(len(full[0]))]
    checks = {
        "nuisance_rank": rank_exact(nuisance),
        "full_rank": rank_exact(full),
        "three_cell_nuisance_rank": rank_exact([row[:-1] for row in full[:3]]),
        "three_cell_full_rank": rank_exact(full[:3]),
        "unchanged_separation_nuisance_rank": rank_exact([r[:-1] for r in no_interaction]),
        "unchanged_separation_full_rank": rank_exact(no_interaction),
        "object_specific_q_nuisance_rank": rank_exact([r[:-1] for r in per_object]),
        "object_specific_q_full_rank": rank_exact(per_object),
        "528_absent_full_rank": rank_exact(design(include_528=True)),
        "altitude_interaction_km": delta_h,
        "contrast_columns": contrast,
    }
    assert checks == {
        "nuisance_rank": 3, "full_rank": 4,
        "three_cell_nuisance_rank": 3, "three_cell_full_rank": 3,
        "unchanged_separation_nuisance_rank": 3,
        "unchanged_separation_full_rank": 3,
        "object_specific_q_nuisance_rank": 4,
        "object_specific_q_full_rank": 4, "528_absent_full_rank": 4,
        "altitude_interaction_km": 30,
        "contrast_columns": [0, 0, 0, 0, 0, -30],
    }
    return {
        "id": "C241-P29",
        "status": "SYNTHETIC_CONDITIONAL_DESIGN_NOT_HISTORICAL_MEASUREMENT",
        "source_inventory": archive_snapshot(),
        "design_assumptions": [
            "Two distinct bodies each observed at two shared epochs, with true altitude and isolated drag acceleration known.",
            "Log-normalized drag = log A + log B_object + log q_epoch - (h-h0)/H.",
            "Positive common temporal multiplier q_epoch across both objects, constant positive B per object.",
            "Source-linked calibration, physical propagation, sensor errors and independence are NOT available for 1963.",
        ],
        "synthetic_cells_object_epoch_altitude_km": [list(c) for c in CELLS],
        "interaction": {
            "contrast": "-z527_0+z529_0+z527_1-z529_1",
            "weights": list(WEIGHTS),
            "delta_relative_altitude_km": delta_h,
            "coefficient_of_inverse_scale_height_km": -delta_h,
            "nuisance_coefficients_exactly_zero": True,
        },
        "exact_rank_diagnostic": checks,
        "fourth_cell": "Required to identify 1/H under two arbitrary shared epoch factors; not a prospective predictive holdout.",
        "missing_528": "Neither q(t) cancellation nor 527/529 controls identifies B_528 absent 528 measurements.",
        "historical_mcmc": "NOT_RUN",
        "historical_domain_reduction": "NOT_EVALUABLE",
        "active_constraint": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = json.dumps(build_report(), ensure_ascii=False, indent=2) + "\n"
    if args.write:
        OUTPUT.write_text(payload)
        print(f"WROTE {OUTPUT.relative_to(ROOT)}")
    elif args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text() != payload:
            raise SystemExit("FAIL: committed C241-P29 report differs from source-derived result")
        print("PASS: C241-P29 exact rank, archive guard and committed report")
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
